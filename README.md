# Orion Terrametrics Africa Limited — Production Website

This repository contains the production website for Orion Terrametrics Africa Limited (OTAL). It hosts the company's public-facing site used for presenting services, projects, contact information, and news.

Live site
---------
https://orionterrametrics.co.ke

Quick links
-----------
- Repository: https://github.com/godwinmurithi/otal_web_main
- Maintainer: @godwinmurithi

Table of contents
-----------------
- About
- Features
- Technology stack
- Getting started (development)
- Environment variables
- Build & deploy (production)
- Tests
- Maintenance & monitoring
- Contributing
- Security
- License
- Contact

About
-----
Orion Terrametrics Africa Limited (OTAL) provides geospatial, surveying, GIS, and remote sensing solutions. This repository contains the company's production website used to showcase services, projects, team information, and to provide contact channels for clients and partners.

Features
--------
- Company overview, services, and portfolio pages
- Responsive, mobile-first UI
- SEO-friendly structure and metadata
- Contact form or integrations with a form provider
- Blog / news section (optional)
- Accessibility and basic performance optimizations
- Hooks for analytics and error monitoring

Technology stack
----------------
Update this section to reflect the actual stack used in the repository. Common examples:
- Frontend: Next.js / React / Vue / Nuxt / plain HTML/CSS/JS
- Styling: Tailwind CSS / SASS / CSS modules
- Backend (if present): Node.js / Express / PHP / Django / Laravel
- Hosting: Vercel / Netlify / GitHub Pages / VPS
- CI/CD: GitHub Actions, CircleCI
- Monitoring: Sentry, LogRocket

Getting started (development)
-----------------------------
Clone the repository

    git clone https://github.com/godwinmurithi/otal_web_main.git
    cd otal_web_main

Install dependencies

- If this is a Node-based project:

    npm install
    # or
    yarn install

Run the development server

- Typical commands (update according to the project):

    npm run dev
    # or
    npm start

Open the site locally at http://localhost:3000 (or the port configured by the project).

Environment variables
---------------------
Create a .env file from .env.example (do not commit secrets).

Suggested variables (update to project needs):

- NODE_ENV=development
- PORT=3000
- NEXT_PUBLIC_API_URL=
- CONTACT_FORM_ENDPOINT=
- ANALYTICS_ID=
- SENTRY_DSN=

Add a .env.example file listing variable names and placeholder values to help contributors.

Build & deploy (production)
---------------------------
Build the production artifacts (common commands — replace with project's commands):

    npm run build
    npm run start

Deployment options

- Vercel / Netlify: Connect the repository, set environment variables in the dashboard, and configure the build command and publish directory.
- GitHub Actions: Add a workflow to build and deploy on push to the production branch (e.g., main).
- VPS: Build artifacts and deploy to the server, or use a CI process to deploy.

Post-deploy checklist

- Verify HTTPS (Let’s Encrypt or managed certs)
- Confirm analytics and monitoring are configured for production
- Check robots.txt and sitemap.xml
- Verify redirects and canonical URLs

Tests
-----
Run unit and integration tests according to the project setup. Common commands:

    npm test
    npm run lint

Add or update test instructions to reflect the repository's test setup.

Maintenance & monitoring
------------------------
- Error tracking: Sentry, LogRocket, or similar
- Uptime monitoring: UptimeRobot, Pingdom
- Performance: Lighthouse, WebPageTest
- Regular dependency updates: Dependabot or Renovate
- Backup strategy for any server-side data

Contributing
------------
Contributions are welcome. Please follow this workflow:

1. Fork the repo
2. Create a feature branch: git checkout -b feat/your-feature
3. Make changes and add tests
4. Run linting and tests
5. Open a pull request with a clear description and screenshots if applicable

Consider adding CONTRIBUTING.md and a PR template to guide contributors.

Security
--------
If you discover a security vulnerability, please report it privately to the maintainers. Do not create a public issue for security-sensitive information.

License
-------
(Choose a license for this repository, for example MIT)

Contact
-------
- Orion Terrametrics Africa Limited
- Maintainer: @godwinmurithi
- Email: (add company contact email)
- Website: https://orionterrametrics.co.ke

Notes & next steps
------------------
- Replace placeholders (tech stack, contact email, license) with the actual project values.
- Add screenshots or a demo GIF to the README to showcase the site.
- Add a .env.example and CONTRIBUTING.md if desired.
