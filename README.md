# Byzantine Condictiones

Data, rulemap and results for *A Rule-Based Mapping of the Byzantine Classification of the Condictiones in D. 12.1*.

We classify *condictiones* in Justinian's *Digest* according to Stephanus' five-fold scheme, using a neuro-symbolic Rulemap: a propositional tree whose leaves are decided by an LLM.

## Files

| File | Contents |
|---|---|
| `crawlandchunk_all.py` | Extracts every *Digest* subsection containing a `condic-` form from the Grenoble edition (books 1–50). Output: the fragment corpus. |
| `Byzantine_Condictiones_-_REWORK_295.xml` | The Rulemap: branches, operators and the query definition of every element. |
| `16_references_gold.xlsx` | Gold standard for Stephanus' cross-references outside D. 12.1 (16 references, 10 fragments). |
| `Results_XLSX_10_07_2026_TESTSET.xlsx` | Blind run on the held-out half of D. 12.1. |
| `Results_XLSX_18_08_2026_OTHERMODELS.xlsx` | Same configuration under four models, 25 labelled fragments. |
| `Results_reruns_inclzeroshot.xlsx` | Five repetitions per configuration, with the zero-shot ablation. `Gesamt` = summary, `Einzeln` = per fragment. |
| `Final_Results_260805.xlsx` | Full corpus run: 328 fragments, 37 books. |
| `HTML_Case_Analysis/` | Per-fragment reports: the verdict and justification of every leaf behind each classification. |

## Pipeline

1. `crawlandchunk_all.py` builds the corpus from the Grenoble *Corpus Iuris Civilis*.
2. The Rulemap is executed per fragment; each leaf is one model call returning a binary verdict plus a justification.
3. Branch logic derives the *condictio*; the general actions are suppressed where a specific one fires.

Runs use GPT-5.5, temperature 0.1, top-p 1e-5, fixed seed, extended reasoning off. Rulemaps can be inspected at <https://builder.rulemapping.org/>.
