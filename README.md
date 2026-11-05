# Joyful Responsible Abundance

An educational website connecting Luke Nathan Hayes’s whole-system proposal with the reviewed paper on superintelligence and Australian sovereignty. It introduces the ideas for readers with no prior context, then gives them source documents, dated references, public project links and tools for exploring the scale.

Public site: https://auraofintelligence.github.io/joyful-responsible-abundance/

Repository: https://github.com/auraofintelligence/joyful-responsible-abundance

The visual design uses full-width photographic heroes, a dark reading palette and a restrained seam of warm and cool light. The opening contrasts pressures in the status quo with the capacities people can choose to build.

## Read and explore

- `start-here.html` introduces the purpose and the whole-system connections.
- `explore.html` maps every component of the whole-system preview.
- `people.html`, `capacity.html`, `civic.html` and `world.html` present the full preview in four reading paths.
- `sovereignty.html` opens six educational chapters about the AI race and Australian choices.
- `sovereignty-paper.html` contains the complete reviewed paper with its inline source links and calculation method.
- `tools.html` contains a compute-cost calculator, a connection tree and an electricity comparison calculator.
- `library.html` searches the sources from both papers. `projects.html` links the related public pages and repositories.
- `glossary.html`, `site-map.html` and `about.html` provide definitions, navigation, authorship and image credits.

The two supplied Word documents are in `documents/`. Evidence in the sovereignty paper is dated 5 November 2026. Company targets remain attributed, and its future figures are conditional scenarios. The whole-system preview reflects the 22-song album, household bill de-slop, the GAJRA Earth public watch and the proposed global festival in July 2035 marking Live Aid’s 50th anniversary.

## Run locally

Serve this folder with a static server, for example `python -m http.server 8769`, and visit `http://localhost:8769/`. The pages, navigation and references work without a framework or dependency installation. JavaScript enhances the calculators, connection selector and local search. No visitor data is submitted by these tools.

## Edit and rebuild

The authored data is in `data/preview.json` and `data/sovereignty.json`. Shared templates and additional educational copy are in `build.py`. Run `python build.py` after content changes. `assets/site.css` and `assets/site.js` hold the responsive design and browser interactions. Optimised WebP assets are committed. Locally retained original generation PNGs are ignored.

Check internal links and anchors, keyboard navigation, mobile widths, the two calculators, search and the generated sitemap after changes. Keep the chapter content available without JavaScript. Preserve all source dates and distinctions between working tools, proposals, announced targets and conditional scenarios.

Every page has shared footer navigation following the order in `data/page-index.json`, with destination titles, Previous and Next labels, and a page count. The homepage starts the sequence with a site-map option; the final site-map page provides a return to Home.

## Publishing and discovery

GitHub Pages serves the repository root on `main`. The repository includes `.nojekyll`, canonical URLs, social sharing metadata, a favicon, `robots.txt`, `sitemap.xml`, `llms.txt` and a human-readable site map.

Suggested description: Educational guide to Joyful Responsible Abundance, superintelligence and Australian sovereignty. Connected proposals, public projects, source papers, calculators and pathways from everyday agency to global cooperation.

Topics: `joyful-responsible-abundance`, `artificial-intelligence`, `ai-alignment`, `sovereign-compute`, `australia`, `community`, `cooperatives`, `civic-tech`, `education`, `github-pages`, `public-source`, `accessibility`, `built-2026-11-05`.

## Images and rights

Four AI-generated concept scenes illustrate possible settings for the proposals. Real Minjerribah photographs are separately identified and credited on the About page. Image provenance is recorded in `assets/images/image-credits.json`.

Original material is by Luke Nathan Hayes / Strange But True / Aura of Intelligence and follows `LICENCE.md`, the Strange But True Public Source Licence. Third-party photographs and linked source works retain their own rights and licences.
