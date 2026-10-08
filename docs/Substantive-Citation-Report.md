# Substantive Citation Report

Prepared October 7, 2026. 8 selected articles; 36 marked discussion pages.

Eight articles selected by conference venue and/or citation count, documenting methodological adaptation, technical exposition, comparison and quantizer-design connections.

This report includes articles published in conferences rated ICORE2026 A* and/or carrying at least 100 Google Scholar citations in the saved snapshot. Counts belong to the citing articles' Scholar records or version clusters. Each entry identifies its reviewed publication version and the contribution supported by the source passage.

[Report PDF](Substantive-Citation-Report.pdf) · [Marked discussions, pages 1–36](Selected-Discussion-Pages.pdf#page=1) · [Interactive map](Comprehensive-Citation-Map.html)

Article numbers identify the corresponding marked files.

## Substantive citations

| Article | Title / venue | Scholar citations | Discussion pages |
|---:|---|---:|---|
| 1 | [Understanding and Overcoming the Challenges of Efficient Transformer Quantization](https://aclanthology.org/2021.emnlp-main.627.pdf)<br>EMNLP 2021 | [271](https://scholar.google.com/scholar?cites=8710219284475667501&as_sdt=5,44&sciodt=0,44&hl=en&num=20) | 3, 7 |
| 2 | [Up or Down? Adaptive Rounding for Post-Training Quantization](https://proceedings.mlr.press/v119/nagel20a/nagel20a.pdf)<br>ICML 2020 | [1,224](https://scholar.google.com/scholar?cites=15168731053848628528&as_sdt=5,44&sciodt=0,44&hl=en&num=20) | 5 |
| 3 | [A White Paper on Neural Network Quantization](https://arxiv.org/pdf/2106.08295)<br>arXiv / Qualcomm white paper, 2021 | [1,362](https://scholar.google.com/scholar?cites=3269278865430026974&as_sdt=5,44&sciodt=0,44&hl=en&num=20) | 20, 22 |
| 4 | [Mixed Precision DNNs: All you need is a good parametrization](https://arxiv.org/pdf/1905.11452)<br>ICLR 2020 | [230](https://scholar.google.com/scholar?cites=4816865987143977033&as_sdt=5,44&sciodt=0,44&hl=en&num=20) | 1–2, 4–5, 8–9 |
| 5 | [Bayesian Bits: Unifying Quantization and Pruning](https://proceedings.neurips.cc/paper/2020/file/3f13cf4ddf6fc50c0d39a1d5aeb57dd8-Paper.pdf)<br>NeurIPS 2020 | [207](https://scholar.google.com/scholar?cites=5274328621855648354&as_sdt=5,44&sciodt=0,44&hl=en&num=20) | 6, 8 |
| 6 | [Bringing AI to edge: From deep learning’s perspective](https://arxiv.org/pdf/2011.14808)<br>Neurocomputing 485 (2022) | [247](https://scholar.google.com/scholar?cites=14516287917516942788&as_sdt=5,44&sciodt=0,44&hl=en) | 8–9 |
| 7 | [HMQ: Hardware Friendly Mixed Precision Quantization Block for CNNs](https://arxiv.org/pdf/2007.09952)<br>ECCV 2020 | [95](https://scholar.google.com/scholar?cites=8154175130422296943&as_sdt=5,45&sciodt=0,45&hl=en) | 1–4 |
| 8 | [QKD: Quantization-aware Knowledge Distillation](https://arxiv.org/pdf/1911.12491)<br>arXiv preprint, 2019 | [125](https://scholar.google.com/scholar?cites=14630303220790911427&as_sdt=2005&sciodt=0,5&hl=en&num=20) | 2–3, 7 |

## Substantive citations — article discussions

## 1. Understanding and Overcoming the Challenges of Efficient Transformer Quantization

Yelysei Bondarenko; Markus Nagel; Tijmen Blankevoort

EMNLP 2021 · 271 Google Scholar citations

Qualcomm researchers explicitly adapt the jointly credited LSQ/TQT procedure from Esser et al. and Jain et al. to learn weight and activation ranges for BERT-like transformer models.

**Methodological adaptation:** Adapts trainable weight and activation ranges to BERT-like models, jointly crediting the procedures of Jain et al. and Esser et al.

**Authorship link:** Jain, Gural, Wu and Dick (2019), Trained uniform quantization for accurate and efficient neural network inference on fixed-point hardware. [Bibliography p. 11](Marked-Articles/01-Transformer-Quantization-MARKED.pdf#page=11).

**Reviewed version:** Published proceedings PDF. **Source:** E-0046; Physical PDF pp. 3, 7, learnable weight/activation ranges and their adaptation to transformers; bibliography p. 11 / printed p. 7957. Count: E-0430, data.organic_results[6].inline_links.cited_by.total.

[Original article](https://aclanthology.org/2021.emnlp-main.627.pdf) · [Scholar cited-by list](https://scholar.google.com/scholar?cites=8710219284475667501&as_sdt=5,44&sciodt=0,44&hl=en&num=20)

## 2. Up or Down? Adaptive Rounding for Post-Training Quantization

Markus Nagel; Rana Ali Amjad; Mart van Baalen; Christos Louizos; Tijmen Blankevoort

ICML 2020 · 1,224 Google Scholar citations

The AdaRound paper names Jain et al., alongside Esser et al., when explaining how quantization ranges can be learned during training instead of being set manually.

**Named technical recognition:** Explains the contribution of learning quantization ranges in the related-work analysis of AdaRound, with joint credit to Jain et al. and Esser et al.

**Authorship link:** Jain, Gural, Wu and Dick (2019), Trained uniform quantization for accurate and efficient neural network inference on fixed-point hardware. [Bibliography p. 10](Marked-Articles/02-AdaRound-MARKED.pdf#page=10).

**Reviewed version:** Published PMLR PDF; physical pages retained. **Source:** E-0321; Physical PDF p. 5, section 4 Background and related work; bibliography physical p. 10. Count: E-0430, data.organic_results[2].inline_links.cited_by.total.

[Original article](https://proceedings.mlr.press/v119/nagel20a/nagel20a.pdf) · [Scholar cited-by list](https://scholar.google.com/scholar?cites=15168731053848628528&as_sdt=5,44&sciodt=0,44&hl=en&num=20)

## 3. A White Paper on Neural Network Quantization

Markus Nagel; Marios Fournarakis; Rana Ali Amjad; Yelysei Bondarenko; Mart van Baalen; Tijmen Blankevoort

arXiv / Qualcomm white paper, 2021 · 1,362 Google Scholar citations

The quantization white paper explains learning quantization parameters through the straight-through estimator, credits Jain et al. alongside Esser et al. and Bhalgat et al., and develops the corresponding gradient derivation.

**Technical exposition:** Develops the gradient calculation for learnable quantization parameters after crediting Jain et al., Esser et al. and Bhalgat et al.

**Authorship link:** Jain, Gural, Wu and Dick (2019), Trained uniform quantization for accurate and efficient neural network inference on fixed-point hardware. [Bibliography p. 26](Marked-Articles/03-White-Paper-MARKED.pdf#page=26).

**Reviewed version:** Reviewed arXiv white paper. **Source:** E-0090; Physical PDF pp. 20, 22, gradient derivation and QAT initialization; bibliography p. 26. Count: E-0430, data.organic_results[1].inline_links.cited_by.total.

[Original article](https://arxiv.org/pdf/2106.08295) · [Scholar cited-by list](https://scholar.google.com/scholar?cites=3269278865430026974&as_sdt=5,44&sciodt=0,44&hl=en&num=20)

## 4. Mixed Precision DNNs: All you need is a good parametrization

Stefan Uhlich; Lukas Mauch; Fabien Cardinaux; Kazuki Yoshiyama; Javier Alonso García; Stephen Tiedemann; Thomas Kemp; Akira Nakamura

ICLR 2020 · 230 Google Scholar citations

Sony researchers describe TQT's trained dynamic range and train a TQT-style fixed-bitwidth model for their experimental comparison with mixed-precision quantization.

**Implemented experimental comparison:** Trains a TQT-style model as a fixed-bitwidth benchmark for the authors’ concurrently developed mixed-precision method.

**Authorship link:** Jain, Gural, Wu and Dick (2019), Trained uniform quantization for accurate and efficient neural network inference on fixed-point hardware. [Bibliography p. 10](Marked-Articles/04-Mixed-Precision-DNNs-MARKED.pdf#page=10).

**Reviewed version:** Author-hosted arXiv copy bearing ICLR 2020 publication header. **Source:** E-0087; PDF/printed pp. 1–2, 4–5, 8–9, introduction, quantizer constraints, experimental setup and TQT result rows; bibliography p. 10. Count: E-0430, data.organic_results[11].inline_links.cited_by.total.

[Original article](https://arxiv.org/pdf/1905.11452) · [Scholar cited-by list](https://scholar.google.com/scholar?cites=4816865987143977033&as_sdt=5,44&sciodt=0,44&hl=en&num=20)

## 5. Bayesian Bits: Unifying Quantization and Pruning

Mart van Baalen; Christos Louizos; Markus Nagel; Rana Ali Amjad; Ying Wang; Tijmen Blankevoort; Max Welling

NeurIPS 2020 · 207 Google Scholar citations

The Bayesian Bits authors credit two papers with independently introducing joint learning of scale and model parameters. Reference [15] identifies the TQT work by Jain, Gural, Wu and Dick.

**Attribution of a research contribution:** Credits reference [15] as one of two papers that independently introduced joint learning of quantization scale and network parameters.

**Authorship link:** Jain, Gural, Wu and Dick (2019), Trained uniform quantization for accurate and efficient neural network inference on fixed-point hardware. [Bibliography p. 10](Marked-Articles/05-Bayesian-Bits-MARKED.pdf#page=10).

**Reviewed version:** Published NeurIPS PDF. **Source:** E-0324; PDF/printed pp. 6, 8, scale learning and TQT in Figure 2b and its caption; bibliography p. 10, reference [15]. Count: E-0430, data.organic_results[9].inline_links.cited_by.total.

[Original article](https://proceedings.neurips.cc/paper/2020/file/3f13cf4ddf6fc50c0d39a1d5aeb57dd8-Paper.pdf) · [Scholar cited-by list](https://scholar.google.com/scholar?cites=5274328621855648354&as_sdt=5,44&sciodt=0,44&hl=en&num=20)

## 6. Bringing AI to edge: From deep learning’s perspective

Di Liu; Hao Kong; Xiangzhong Luo; Weichen Liu; Ravi Subramaniam

Neurocomputing 485 (2022) · 247 Google Scholar citations

The edge-AI survey gives Jain et al. a dedicated methodological description of trained uniform quantization for accurate and efficient neural-network inference on fixed-point hardware.

**Named survey discussion:** Explains trained uniform quantization for fixed-point inference in a survey of deep learning at the edge; reference [121] identifies Jain et al.’s paper.

**Authorship link:** Jain, Gural, Wu and Dick (2019), Trained uniform quantization for accurate and efficient neural network inference on fixed-point hardware. [Bibliography p. 20](Marked-Articles/06-Bringing-AI-to-Edge-MARKED.pdf#page=20).

**Reviewed version:** arXiv author manuscript; journal publication verified separately. **Source:** E-0044; PDF/printed pp. 8–9, TQT comparison-table row and named quantization discussion; bibliography p. 20, reference [121]; affiliations p. 1. Count: E-0366, data.organic_results[0].inline_links.cited_by.total.

[Original article](https://arxiv.org/pdf/2011.14808) · [Scholar cited-by list](https://scholar.google.com/scholar?cites=14516287917516942788&as_sdt=5,44&sciodt=0,44&hl=en)

## 7. HMQ: Hardware Friendly Mixed Precision Quantization Block for CNNs

Hai Victor Habi; Roy H. Jennings; Arnon Netzer

ECCV 2020 · 95 Google Scholar citations

HMQ states that the quantizer it uses is similar to the quantizer of Jain et al. identified by reference [24], then presents its hardware-friendly mixed-precision formulation.

**Quantizer-design connection:** Identifies the quantizer in reference [24] as similar to the one used in HMQ, followed by signed and unsigned quantizer definitions in equations 2 and 3.

**Authorship link:** Jain, Gural, Wu and Dick (2019), Trained quantization thresholds for accurate and efficient fixed-point inference of deep neural networks. [Bibliography p. 17](Marked-Articles/07-HMQ-MARKED.pdf#page=17).

**Reviewed version:** Author arXiv manuscript; ECCV publication verified separately. **Source:** E-0043; Physical PDF pp. 1–4, hardware-friendly quantization citations and quantizer definition; bibliography p. 17. Count: E-0368, data.organic_results[0].inline_links.cited_by.total.

[Original article](https://arxiv.org/pdf/2007.09952) · [Scholar cited-by list](https://scholar.google.com/scholar?cites=8154175130422296943&as_sdt=5,45&sciodt=0,45&hl=en)

## 8. QKD: Quantization-aware Knowledge Distillation

Jangho Kim; Yash Bhalgat; Jinwon Lee; Chirag Patel; Nojun Kwak

arXiv preprint, 2019 · 125 Google Scholar citations

QKD describes trainable intervals in LSQ and TQT alongside other trainable quantization approaches, and states that it uses these approaches in its baseline before applying knowledge distillation.

**Use in a research implementation:** Includes TQT [17] among the jointly credited trainable quantization approaches used in the baseline. The reported results concern quantization combined with knowledge distillation.

**Authorship link:** Jain, Gural, Wu and Dick (2019), Trained quantization thresholds for accurate and efficient fixed-point inference of deep neural networks. [Bibliography p. 9](Marked-Articles/08-QKD-MARKED.pdf#page=9).

**Reviewed version:** Reviewed arXiv manuscript. **Source:** E-0056; Physical PDF pp. 2–3, 7, trainable intervals, dequantization and depthwise-layer sensitivity; bibliography p. 9, reference [17]. Count: E-0378, data.organic_results[0].inline_links.cited_by.total.

[Original article](https://arxiv.org/pdf/1911.12491) · [Scholar cited-by list](https://scholar.google.com/scholar?cites=14630303220790911427&as_sdt=2005&sciodt=0,5&hl=en&num=20)

## International reach and source coverage

The wider survey maps 146 citing works across 29 countries/territories, with 157 institution/location entries. The inventory retains 323 works from 337 archived Scholar records; the saved profile records 354 citations.

Publication affiliations establish geographic reach, including coauthor- and employer-linked works. [Coverage by publication](Coverage-by-Publication.csv) records retrieval and affiliation-review totals. Article-specific passages establish the documented scholarly contribution or connection.
