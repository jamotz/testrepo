// Résumé content, the single source for both versions:
//   /resume (web, portfolio styling) and public/resume/jack-motzkin-resume.pdf (one page,
//   rendered from the same page's print styles by tools/resume_pdf.mjs).
// Source: Jack's LinkedIn export (Oct 2026) plus the case studies. Keep it to one page:
// tools/resume_pdf.mjs fails if the PDF runs onto a second page.

export const RESUME_DATA = {
  name: 'Jack Motzkin',
  headline: 'UX Researcher & Designer · Business & Customer Analysis',
  location: 'Greater Phoenix Area, AZ',
  email: 'jackmotzkin@icloud.com',
  phone: null,   // e.g. '(480) 555-0123'; shown in the contact line once set
  links: [
    { label: 'jackmotzkin.com', href: 'https://jackmotzkin.com' },
    { label: 'linkedin.com/in/jack-motzkin', href: 'https://www.linkedin.com/in/jack-motzkin/' },
  ],

  summary:
    'Entry-level UX researcher with a B.A. in Psychology and certifications in UX (BCS), data science (IBM) and business analysis. ' +
    'Led mixed-methods research for Oxfam Australia, Origins Cannabis and Premier Packout, and presented the findings to a COO and a CEO. ' +
    'Seeking UX research, business analyst or customer insights roles.',

  // newest first, as a résumé reads
  experience: [
    {
      org: 'Veeam Software', where: 'Tempe, AZ',
      roles: [
        { title: 'Site Experience Specialist II', dates: 'Feb 2026 – Present' },
        { title: 'Site Experience Specialist I', dates: 'Feb 2025 – Feb 2026' },
      ],
      bullets: [
        'Surveyed employees on their time in the office and turned the findings into changes to the workplace and its services.',
        'Helped facilitate office buildouts and furniture exchanges around employee needs, aligning branding, design and operations.',
        'Track purchasing and expenses through a purchase-order system, keeping budgets, approvals and records accurate.',
        'Coordinate vendors and contractors, and resolve facility, security and logistics issues before they disrupt staff.',
      ],
    },
    {
      org: 'Premier Packout', where: 'Scottsdale, AZ',
      roles: [{ title: 'Project Specialist · CX Analyst', dates: 'Apr 2024 – Jan 2025' }],
      bullets: [
        'Partnered with the CEO of a fire and flood pack-out company, which works closely with insurers, to map the customer journey.',
        'Ran interviews, shadowed crews, and analyzed a 36-homeowner survey and online reviews to set a 56% satisfaction baseline.',
        'Built an eight-phase journey map and audited the website, finding pain points across packing, storage, cleaning and pack-back.',
        'Delivered a research report and white-glove service plan to the CEO across the website, staff and fleet, and operations.',
      ],
    },
    {
      org: 'Origins Cannabis', where: 'Redmond, WA',
      roles: [{ title: 'Budtender · UX Researcher & Designer', dates: 'Jul 2022 – May 2023' }],
      bullets: [
        'Recruited customers in store for surveys and interviews on why the app failed them; built personas and a competitive SWOT.',
        'Concept- and A/B-tested product displays, then usability-tested a leveled filter system and a reorganized shop and home.',
        'Designed 20+ high-fidelity frames in Figma and analyzed survey data, customer paths and IA in FigJam.',
        'Presented a research report to the shareholders and COO; worked with marketing and operations on in-store sales.',
      ],
    },
    {
      org: 'PeakXD · Oxfam Australia', where: 'Remote',
      roles: [{ title: 'UX Research & Design Certification Project', dates: 'Jul – Dec 2022' }],
      bullets: [
        'Redesigned the information architecture of Oxfam Australia’s support pages and MyOxfam portal.',
        'Ran user interviews, built a persona, card-sorted the navigation and tree-tested it in Optimal Workshop.',
        'Wireframed and prototyped in Figma, usability-tested the design, and presented it to stakeholders.',
      ],
    },
  ],
  earlier:
    'Earlier experience (2016–2021): five roles in food service, construction and aquatics, including shift lead and trainer, lifeguard and swim instructor.',

  skills: [
    { k: 'Research', v: 'User interviews, usability testing, surveys, card sorting, tree testing, concept & A/B testing, competitive analysis, mixed methods' },
    { k: 'Analysis', v: 'Discussion guides, intercept recruiting, facilitation, synthesis, survey & data analysis, personas, journey mapping' },
    { k: 'Communication', v: 'Research reports; presenting to stakeholders, a CEO and a COO' },
    { k: 'Tools', v: 'Figma, FigJam, Optimal Workshop; coursework in SQL, Excel and data visualization' },
  ],

  education: [
    { school: 'University of Arizona', what: 'B.A. Psychology, minor in Sociology', dates: '2018 – 2022' },
    { school: 'Bellevue College', what: 'A.A. Arts & Sciences', dates: '2016 – 2018' },
  ],
  certifications: [
    'BCS Foundation Certificate in User Experience',
    'IBM Data Science Professional Certificate',
    'Career Essentials in Business Analysis (Microsoft & LinkedIn)',
    'Career Essentials in Generative AI (Microsoft & LinkedIn)',
    'Design Psychology: Master the Art and Science of UX Design',
  ],
  awards: 'Eagle Scout · Spanish and Italian (elementary)',
};
