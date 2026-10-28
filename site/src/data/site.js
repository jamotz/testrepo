// One place for the details that repeat across the site (nav, cards, About,
// Contact, footer). Change them here, not in the components.

export const EMAIL = 'Jackmotzkin@icloud.com';
export const LINKEDIN = 'https://www.linkedin.com/in/jack-motzkin/';

// Résumé — not ready yet. Set `pdf` to the downloadable file (e.g. '/resume/jack-motzkin-resume.pdf'
// in public/) and `web` to the themed page (e.g. '/resume'); every résumé link on the site
// switches from "coming soon" to a real link once these are set.
export const RESUME = { pdf: null, web: null };

// Skills, grouped as on the landing page (foot of About), in the words job posts use.
// Each case study's own list is in methods.json.
export const SKILLS = [
  { group: 'Research methods', items: ['User interviews', 'Usability testing', 'Surveys', 'Card sorting', 'Tree testing', 'Concept testing', 'A/B testing', 'Competitive analysis', 'Mixed methods'] },
  { group: 'Planning & analysis', items: ['Research plans & discussion guides', 'In-person intercept recruiting', 'Session facilitation', 'Synthesis', 'Survey & data analysis', 'Personas', 'Journey mapping'] },
  { group: 'Communication', items: ['Research reports', 'Presenting to stakeholders, CEO & COO'] },
  { group: 'Tools', items: ['Figma', 'FigJam', 'Optimal Workshop'] },
];

// Projects, in display order. `href: null` = page not live yet (shown as "coming soon").
export const PROJECTS = [
  {
    slug: 'oxfam', href: '/work/oxfam', accent: 'var(--ac-oxfam)',
    logo: '/brand/clients/oxfam.svg', logoAlt: 'Oxfam',
    title: 'Oxfam Support Redesign', short: 'Oxfam Australia',
    role: 'UX Research & Design', client: 'Oxfam Australia', location: 'Remote · Melbourne, AU',
    desc: 'Rebuilt Oxfam Australia’s support pages and the MyOxfam portal: new information architecture, wireframes, usability testing, and a final design presented to stakeholders.',
  },
  {
    slug: 'origins', href: '/work/origins', accent: 'var(--ac-origins)',
    logo: '/brand/clients/origins.svg', logoAlt: 'Origins',
    title: 'Origins App Redesign', short: 'Origins Cannabis',
    role: 'UX Research & Design', client: 'Origins Cannabis', location: 'Redmond, WA',
    desc: 'Interviewed dispensary customers in person to learn why the app failed them, then rebuilt its product display and information architecture and tested it hands-on.',
  },
  {
    slug: 'premier', href: '/work/premier', accent: 'var(--ac-premier)',
    logo: '/brand/clients/premier.png', logoAlt: 'Premier Packout Service',
    title: 'Premier Business Analysis', short: 'Premier Packout',
    role: 'Business Analysis', client: 'Premier Packout', location: 'Scottsdale, AZ',
    desc: 'Worked with the CEO of a fire and flood pack-out company that partners closely with insurance companies, mapping how homeowners experience a pack-out from first call to final delivery and turning the pain points into service changes.',
  },
];
