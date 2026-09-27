---
title: 'RingSentry: Reproducible preprocessing and quality control for two-dimensional X-ray diffraction images'
tags:
  - Python
  - diffraction
  - detector images
  - quality control
  - scientific image processing
authors:
  - name: Delun Gong
    orcid: 0000-0001-7877-7707
    email: dlgong17s@imr.ac.cn
    affiliation: 1
    corresponding: true
affiliations:
  - index: 1
    name: Institute of Metal Research, Chinese Academy of Sciences, Shenyang 110016, China
date: 27 September 2026
bibliography: paper.bib
---

# Summary

X-ray area detectors produce images that usually need checking and correction before researchers can integrate diffraction patterns or interpret structure. RingSentry is a local desktop application and Python core for this preparation stage. It reads several common detector formats, provides coordinate and final-result previews, applies rule-based quality control (QC) checks, processes batches, and writes reports that record settings and warnings. Quantitative arrays remain separate from display PNGs. The pipeline supports dark and flat correction, background subtraction, regions and masks, intensity limits, hot-pixel suppression, right-angle rotations and flips, block-mean binning, and intensity transforms. A separate CBF workflow can replace a user-confirmed exceptional pixel code in validated copies, but it cannot reconstruct lost detector intensity.

# Statement of need

Area detectors used for SAXS, WAXS, SXRD, and GIWAXS experiments produce large two-dimensional arrays whose data type, metadata, coordinate origin, invalid-value representation, and downstream compatibility vary. Detector data reduction commonly includes dark subtraction, response correction, masking, normalization, and geometry-aware conversion [@boesecke2007reduction]. Errors introduced before integration can be hard to diagnose after a frame has been cropped, rebinned, converted to a display-oriented data type, or detached from the settings used to process it.

RingSentry provides an inspectable preparation stage for researchers moving heterogeneous detector frames between acquisition systems and later analysis software. It combines format-aware loading, preflight sampling, preview, batch execution, and timestamped reports. The software documents coordinate conventions and numerical operation order, warns about non-divisible binning edges and data-type conversions, and keeps quantitative matrices apart from eight-bit RGB views. A deterministic synthetic example exercises the same QC, processing, and writer interfaces as the application and records its seed and parameters in JSON. It is a functional check, not a detector simulation, benchmark, or experimental result.

# State of the field

RingSentry builds on established diffraction software while addressing a narrower stage of the workflow. FabIO provides Python access to many two-dimensional X-ray detector formats [@knudsen2013fabio]; RingSentry uses it for CBF and implements FabIO routes for ADSC/Bruker and Mar-family files alongside dedicated TIFF, HDF5, and EDF handling. Tests currently exercise representative CBF, EDF, TIFF, and HDF5 paths rather than every detector-specific route. pyFAI provides detector calibration and high-performance one- and two-dimensional azimuthal integration, including geometry and pixel-level corrections [@ashiotis2015pyfai]. DIOPTAS similarly combines calibration, integration, and interactive exploration for two-dimensional diffraction data [@prescher2015dioptas]. DAWN 2 provides a broader, extensible platform with configurable processing chains, batch execution, provenance, calibration, and integration [@filik2017dawn]. Pydidas integrates data browsing, calibration, modular workflow setup, processing, and visualization in a GUI whose processing logic is also scriptable [@storm2025pydidas]. Grazing-incidence packages such as INSIGHT and pygid perform reciprocal-space transformations, intensity corrections, one-dimensional cuts, and data reduction [@reus2024insight; @abukaev2026pygid].

RingSentry does not fit detector geometry, perform azimuthal integration, remap GIWAXS data into reciprocal space, identify phases, or refine structures. It instead provides a lightweight local interface and Python core for the earlier preparation stage, with a fixed and testable operation order, separate quantitative and display products, format-aware output semantics, and strict rejection of ambiguous detector stacks. Batch reports expose data-type changes, non-finite values, cropping, and coordinates; separate CBF repair records document project-specific exceptional-value rules. That convention must be confirmed from the acquisition chain and is not a general rule of the CBF/imgCIF specification [@bernstein2006cbf]. RingSentry delegates detector-format decoding to FabIO and leaves calibration and integration to established packages rather than duplicating them.

# Software design

The application separates the `tkinter` interface from numerical and I/O modules. The GUI collects parameters, samples up to five files for preflight QC, dispatches per-file work through a thread pool, and writes a run report. The loader accepts two-dimensional arrays and arrays with singleton axes, rejects non-singleton three-dimensional stacks instead of silently selecting a frame, and returns source metadata. QC computes finite, non-finite, zero, negative, saturation, percentile, and robust extreme-pixel statistics. Each finding includes a level, category, message, and evidence basis; suggestions are advisory.

The processing function converts an input to a two-dimensional `float32` array and applies enabled operations in a documented order: dark subtraction, flat correction, background subtraction, region-of-interest cropping, masking, absolute and percentile limits, negative clipping, local median/MAD hot-pixel suppression, right-angle rotations and flips, block-mean binning, intensity transform, gamma, and normalization. Flat correction expects a relative detector-response map; RingSentry does not normalize raw flat counts automatically. Invalid flat denominators and masked pixels become non-finite values within the pipeline. Writers for compatible floating-point formats preserve these values. CSV and DAT matrices replace non-finite values with zero and add category counts to batch records; external software may render non-finite TIFF values inconsistently. PNG generation follows a distinct fixed-range display path.

![RingSentry architecture. Top: the batch path from GUI inputs through detector I/O, non-mutating QC, fixed-order numerical processing, and format-aware output. Centre: the numerical operation order. Bottom: the independent CBF exceptional-value and ideal planar Q tools.](figures/architecture_workflow.png)

Core behavior is testable without opening the GUI. The test suite covers numerical processing, QC, diffraction geometry, EDF and FabIO interoperability, output semantics, CBF replacement safeguards, interface error handling, metadata consistency, and the end-to-end synthetic example. The example generates two analytic rings with seeded noise, processes the array, and saves quantitative NPY data, a display PNG, and a machine-readable summary.

![(a) Seeded 128 × 128 two-ring synthetic matrix. (b) Result after subtracting a background offset of 35, percentile clipping, negative clipping, 2 × 2 block-mean binning, log1p transformation, and min--max normalization. (c) Radial means normalized separately for display. This functional example is neither experimental data nor a performance benchmark.](figures/synthetic_processing.png)

The design favors an ordered pipeline over an unconstrained plugin graph, reducing ambiguity at the cost of compositional flexibility. Its QC warnings are conservative flags, not scientific interpretations: a global extreme-pixel rule cannot determine whether a bright point is a detector defect or a real diffraction signal. The GUI therefore starts the CBF tool in dry-run mode and requires a non-empty note intended to document the acquisition-chain convention before formal repair. It compares all non-target pixels and reads the saved file back before accepting the output; original-file cleanup is never automated. The result is a QC-oriented copy, not a reconstruction of the intensity lost at an overexposed pixel. The separate Q calculator assumes ideal planar, normal-incidence geometry and does not replace detector calibration.

# Research impact statement

The author reports using RingSentry in the research underlying the Ti-24Nb-4Zr-8Sn study by Gong et al. [@gong2026acta], as confirmed on 27 September 2026. This is an author-confirmed application, not a claim that the article cites the software or that all features in the current candidate were used. The historical revision and operation-to-output mapping remain to be checked against the author's processing records before submission. The repository records this distinction alongside reproducible software-verification examples. Those examples establish specified numerical and software behavior rather than experimental accuracy or independent adoption.


# Software availability

RingSentry is distributed under the MIT License from [GitHub](https://github.com/D-sudoasd/ring-sentry). The current source identifies version 7.0.0; the latest published release remains v6.0.1. The candidate is identified by its source commit. An archive of the final reviewed version will be created after successful review.

# AI usage disclosure

OpenAI Codex assisted earlier repository inspection, requirements and literature organization, tests, documentation, figures and manuscript preparation in July and August 2026. The exact hosted model version for that earlier work was not retained. In September 2026, OpenAI Codex (GPT-6) assisted submission preparation, metadata alignment, research-use documentation and automated verification. The author must review and confirm the complete disclosure and all new AI-assisted outputs before submission.

# Acknowledgements

No external funding was received for this software. There was no sponsor involvement. The author declares no competing interests.

# Author contributions and competing interests

Delun Gong is the sole and corresponding author, as confirmed on 27 September 2026.

# References
