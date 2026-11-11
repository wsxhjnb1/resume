"""Check final PDF text, links, page count, fonts, and page bounds."""
from pathlib import Path
import json
import re
import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "pdf"
QA = ROOT / "tmp" / "pdfs"
QA.mkdir(parents=True, exist_ok=True)
reports = []
for language in ("en", "zh"):
    path = OUTPUT / f"yuhao_xie_resume_{language}.pdf"
    reader = PdfReader(path)
    assert len(reader.pages) == 1, (path.name, len(reader.pages))
    text = "\n".join(page.extract_text() for page in reader.pages)
    readable_text = re.sub(r"\s+", " ", text.replace("‐", "-"))
    for term in ("Yuhao Xie", "EMNLP 2026", "main conference.", "99.3%", "NVIDIA A10", "NVIDIA H100", "40%", "ORCGS", "CUDA/CuTe", "Ampere", "Blackwell", "DGX Spark", "Qwen3-4B", "8K", "32K", "FlashAttention-2", "1.11", "1.13", "LSE"):
        assert term in readable_text, (path.name, term)
    for removed in ("83.1%", "62.5%", "FPGA Accelerator for CNN", "CNN 的 FPGA", "TF32x3", "7.95", "1.47", "119/103", "EAGLE3", "CUDA Graph Padding", "228/256", "accepted", "BF16", "FP16", "36/36", "419", "OrbitCall", "vLLM 0.29", "Qwen2.5-3B", "FA2 Residency Scheduler", "驻留调度与加速"):
        assert removed not in readable_text, (path.name, removed)
    assert "�" not in text, path.name
    compact_text = readable_text.replace(" ", "")
    expected_header_name = "谢雨豪" if language == "zh" else "YuhaoXie"
    assert compact_text.startswith(expected_header_name), (path.name, "header name")
    project_terms = (
        ("TileCadence·FlashAttention-2共享内存调度", "概率块、输出分片和LSE", "13个Qwen3-4B预填充形状", "逐位一致")
        if language == "zh"
        else ("TileCadence—Shared-MemorySchedulingforFlashAttention-2", "probabilitytiles,outputfragments,andLSE", "13Qwen3-4Bprefillshapes", "bitwise-identicaloutputsandLSE")
    )
    for term in project_terms:
        assert term in compact_text, (path.name, term)
    for course in ("EEE3342C", "EEE4346C", "EEL3801C"):
        assert course in compact_text, (path.name, course)
    teaching_terms = ("UCF: Instructor:", "Teaching Assistant:", "Aug. -- Dec. 2026:", "Digital Systems", "Hardware Security and Trusted Circuit Design", "Computer Organization", "Junior Design") if language == "en" else ("中佛罗里达大学：讲师：", "助教：", "2026.08--2026.12", "数字系统", "硬件安全与可信电路设计", "计算机组成", "JuniorDesign")
    for term in teaching_terms:
        normalized_term = re.sub(r"\s+", "", term).replace("--", "–")
        assert normalized_term in compact_text, (path.name, term)
    reviewer_term = "Reviewer:ICLR2027." if language == "en" else "学术服务：ICLR2027审稿人。"
    assert reviewer_term in compact_text, (path.name, "ICLR 2027 reviewer")
    if language == "zh":
        assert "Instructor" not in text, (path.name, "Chinese teaching role translation")
    assert "Fall2026" not in compact_text and "2026年秋季" not in compact_text, (path.name, "removed semester emphasis")
    expected_phone="+8613968074414" if language=="zh" else "+1(689)2208144"
    other_phone="+1(689)2208144" if language=="zh" else "+8613968074414"
    assert expected_phone in compact_text and other_phone not in compact_text, (path.name,"phone")
    expected_links = {
        "mailto:yuhaoxie1999@gmail.com",
        "https://github.com/wsxhjnb1",
        "https://github.com/wsxhjnb1/Beyond-KV-Cache",
        "https://wsxhjnb1.github.io/Beyond-KV-Cache/paper/Beyond.pdf",
        "https://wsxhjnb1.github.io/Beyond-KV-Cache/",
        "https://www.linkedin.com/in/yuhao-xie/",
        "https://github.com/wsxhjnb1/TileCadence",
    }
    actual_links = set()
    font_status = []
    for page in reader.pages:
        for annotation in page.get("/Annots", []):
            action = annotation.get_object().get("/A", {})
            if action.get("/S") == "/URI":
                actual_links.add(str(action["/URI"]))
        for font_ref in page["/Resources"]["/Font"].values():
            font = font_ref.get_object()
            if "/DescendantFonts" in font:
                font = font["/DescendantFonts"][0].get_object()
            descriptor = font.get("/FontDescriptor")
            assert descriptor, path.name
            descriptor = descriptor.get_object()
            embedded = any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3"))
            assert embedded, (path.name, str(font.get("/BaseFont")))
            font_status.append({"name": str(font.get("/BaseFont")), "embedded": embedded})
    assert expected_links <= actual_links, (path.name, actual_links)
    assert not any(old in link.lower() for link in actual_links for old in ("orbitcall", "fa2-residency")), (path.name, actual_links)
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[0]
        visible = [char for char in page.chars if char["text"].strip()]
        bounds = {
            "left": min(char["x0"] for char in visible),
            "right": max(char["x1"] for char in visible),
            "top": min(char["top"] for char in visible),
            "bottom": max(char["bottom"] for char in visible),
        }
        assert bounds["left"] >= 25
        assert bounds["right"] <= page.width - 25
        assert bounds["top"] >= 20
        assert bounds["bottom"] <= page.height - 20
    (QA / f"text_{language}.txt").write_text(text, encoding="utf-8")
    reports.append({"file": path.name, "pages": 1, "links": sorted(actual_links), "fonts": font_status, "text_bounds_points": bounds})
(QA / "verification.json").write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(reports, ensure_ascii=False, indent=2))
