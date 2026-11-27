# Orion TerraMetrics corporate site (enterprise redesign)

Static, dependency-free build of the new orionterrametrics.co.ke. The legacy site in the repo root is untouched until cutover.

- `data.py`: projects, services, industries, products, clients, courses (all from the current site; case studies kept as they are).
- `build.py`: page templates, navigation, search index, sitemap, legacy redirects. Standard library only.
- `src/site.css`, `src/site.js`: design system (navy #07334f, green #0e9637, gold #d4af37; Nunito Sans + Roboto) and behaviour (mega menus, search, filters, tabs, forms).
- `assets/`: WebP images converted from the repo's real project photos and OrionGIS screenshots; client and product logos.
- `tests/qa.mjs`: Playwright crawl of every page at 1440 px and 390 px: JS errors, 4xx assets, horizontal overflow, broken internal links, screenshots.

## Build and preview

    BASE=/company/ PREVIEW=1 python3 build.py     # noindex preview
    rsync -a --delete dist/ /var/lib/docker/volumes/orion_sdh-nginxconfd/_data/company-site/
    node tests/qa.mjs

Preview: https://orionterrametrics.com/company/ (nginx `location ^~ /company/` in orion-root.conf, X-Robots-Tag noindex, no-cache).

Production (at cutover): `BASE=/ PREVIEW=0 python3 build.py`, serve `dist/` as the .co.ke vhost, apply `dist/redirects.json` as nginx 301s, keep /blog until the WordPress posts migrate, and allow CORS from orionterrametrics.co.ke on OrionGIS `/api/contact` (forms post there).

## Forms

All enquiry, careers, partnership, training and enrolment forms POST to OrionGIS `/api/contact` (real email to info@), with client-side validation, a honeypot and an on-screen confirmation. Server-side validation lives in that endpoint. CV upload, vacancy publishing and the admin console are the next phase (Company site editor in Orion Central).
