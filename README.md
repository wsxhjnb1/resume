# Yuhao Xie · 谢雨豪

Research résumé in English and Chinese. Computer Engineering PhD student at the
University of Central Florida, working on efficient LLM inference, KV-cache
quantization, and GPU systems.

**[English résumé (PDF)](yuhao_xie_resume_en.pdf)** ·
**[中文简历（PDF）](yuhao_xie_resume_zh.pdf)** ·
**[Personal website](https://wsxhjnb1.github.io/)**

## Editable sources

- `yuhao_xie_resume_en.tex` — English, one US Letter page.
- `yuhao_xie_resume_zh.tex` — Chinese, one A4 page; display name 谢雨豪.
- `resume_style.sty` — shared typography and layout.

`SHA256SUMS` records the exact PDF and source bytes for the current release.

## Build locally

Use Tectonic or XeLaTeX with Calibri, Segoe UI, DengXian and Microsoft YaHei
installed. Font binaries are not included.

```powershell
./build_resume.ps1
python verify_resume.py
```

The build writes PDFs to `output/pdf/`. After reviewing a new build, replace the
two PDFs at the repository root and the corresponding copies on the personal
website. The verification script checks page count, key text, links, embedded
fonts and page bounds.

## Research

- [Beyond: KV-cache quantization](https://github.com/wsxhjnb1/Beyond-KV-Cache)
- [TileCadence](https://github.com/wsxhjnb1/TileCadence)

Contact: [yuhaoxie1999@gmail.com](mailto:yuhaoxie1999@gmail.com).
