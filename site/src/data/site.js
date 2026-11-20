// One place for the details that repeat across the site (nav, cards, About,
// Contact, footer). Change them here, not in the components.

export const EMAIL = 'Jackmotzkin@icloud.com';
export const LINKEDIN = 'https://www.linkedin.com/in/jack-motzkin/';

// Résumé: the themed web page and its one-page PDF, both built from data/resume.js
// (the PDF by tools/resume_pdf.mjs). Set either to null to hide that link everywhere.
export const RESUME = { pdf: '/resume/jack-motzkin-resume.pdf', web: '/resume' };

// Skills, grouped as on the landing page (foot of About), in the words job posts use.
// Each case study's own list is in methods.json.
export const SKILLS = [
  { group: 'Research methods', items: ['User interviews', 'Usability testing', 'Surveys', 'Card sorting', 'Tree testing', 'Concept testing', 'A/B testing', 'Contextual inquiry', 'Competitive analysis', 'Mixed methods'] },
  { group: 'Planning & analysis', items: ['Research plans & discussion guides', 'In-person intercept recruiting', 'Session facilitation', 'Synthesis', 'Survey & data analysis', 'Personas', 'Journey mapping'] },
  { group: 'Communication', items: ['Research reports', 'Presenting to stakeholders, CEO & COO', 'Stakeholder interviews', 'Actionable recommendations', 'Research storytelling'] },
];

// The "Tools & AI" row under the skill panels. `logo` is a key in data/tool-logos.js;
// a tool without one shows its `mark` (two or three letters) until a logo is added.
// `ai: true` gives the tile the gold accent.
export const TOOLS = [
  { name: 'Figma', logo: 'figma', use: 'Wireframes & prototypes' },
  { name: 'FigJam', mark: 'Fj', use: 'Affinity maps & workshops' },
  { name: 'Optimal Workshop', logo: 'optimalworkshop', use: 'Card sorts & tree tests' },
  { name: 'ChatGPT', logo: 'openai', use: 'Drafting & synthesis support', ai: true },
  { name: 'Claude', logo: 'claude', use: 'Drafting & synthesis support', ai: true },
];
// Below prompt engineering in the Tools & AI panel.
export const DATA_SCIENCE = {
  name: 'Data science foundations',
  badge: 'IBM certified · Foundational',
  desc: 'Introductory coursework in programming, data analysis, visualization and machine learning through the IBM Data Science Professional Certificate.',
  items: ['Python', 'SQL', 'Pandas', 'NumPy', 'Jupyter', 'Matplotlib', 'Scikit-learn'],
};
export const PROMPTING = {
  name: 'Prompt engineering',
  desc: 'Structured prompts with context, constraints and examples, written to get usable research output from ChatGPT and Claude.',
};

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
