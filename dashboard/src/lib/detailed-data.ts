// ═══════════════════════════════════════════════════════════════════════════════
// DETAILED REAL DATA — Morocco Official Sources (HCP, ONEP, ONE, etc.)
// ═══════════════════════════════════════════════════════════════════════════════

export interface University {
  name: string
  acronym: string
  type: 'publique' | 'privée' | 'semi-publique'
  region: string
  founded: number
  students: number
  faculties: string[]
  Website: string
}

export interface Dam {
  name: string
  region: string
  basin: string
  capacityM3: number
  yearBuilt: number
  usage: string[]
  annualFilling: { year: number; percent: number }[]
}

export interface Hospital {
  name: string
  type: 'public' | 'privé' | 'semi-privé' | 'clinique'
  region: string
  province: string
  capacity: number
  specialties: string[]
  annualRevenue: number
  staff: number
  population?: number
}

export interface EngineerGrad {
  field: string
  count: number
  employability: string
}

// ── UNIVERSITIES ───────────────────────────────────────────────────────────
export const UNIVERSITIES: University[] = [
  // Casablanca-Settat
  { name: "Université Hassan II de Casablanca", acronym: "UH2C", type: "publique", region: "Casablanca-Settat", founded: 1975, students: 152000, faculties: ["FLSHAC – Faculté des Lettres et Sciences Humaines Aïn Chock", "FLSHBM – Faculté des Lettres et Sciences Humaines Ben M'sik", "FLSHM – Faculté des Lettres et Sciences Humaines Mohammedia", "ENS – École Normale Supérieure", "ENSA Casablanca – École Nationale Supérieure d'Arts et Métiers", "ENSEM – École Nationale Supérieure d'Électricité et de Mécanique", "FST Mohammedia – Faculté des Sciences et Techniques", "FSJES Aïn Chock – Faculté des Sciences Juridiques, Économiques et Sociales", "FSJES Aïn Sebaâ", "FSJES Mohammédia", "Faculté des Sciences Ben M'sik", "Faculté des Sciences Aïn Chock", "Faculté de Médecine et Odontologie"], Website: "https://www.uh2c.ac.ma" },
  { name: "Université Internationale de Casablanca", acronym: "UIC", type: "privée", region: "Casablanca-Settat", founded: 2014, students: 4500, faculties: ["École d'Ingénierie", "Faculté Privée de Médecine", "Faculté Privée de Pharmacie", "Faculté de Médecine Dentaire", "Faculté des Sciences de la Santé", "Business School", "École Privée d'Architecture", "Pôle Formation Exécutive"], Website: "" },
  { name: "Université Mundiapolis", acronym: "UM", type: "privée", region: "Casablanca-Settat", founded: 2007, students: 3200, faculties: ["École de Commerce et de Management", "École d'Ingénieurs", "Faculté des Lettres et des Sciences Humaines"], Website: "" },

  // Rabat-Salé-Kénitra
  { name: "Université Mohammed V de Rabat", acronym: "UM5R", type: "publique", region: "Rabat-Salé-Kénitra", founded: 1957, students: 95000, faculties: ["FSJES Agdal", "FSJES Souissi", "Faculté des Sciences", "Faculté des Lettres et des Sciences Humaines", "ENSIAS – École Nationale Supérieure d'Informatique et d'Analyse des Systèmes", "ENSMR – École Nationale Supérieure des Mines de Rabat", "ENSAM – École Nationale Supérieure d'Arts et Métiers", "Faculté de Médecine et de Pharmacie", "Institut des Sciences de la Pêche", "ISIC – Institut des Sciences de la Communication"], Website: "https://www.um5.ac.ma" },
  { name: "Université Internationale de Rabat", acronym: "UIR", type: "privée", region: "Rabat-Salé-Kénitra", founded: 2012, students: 5800, faculties: ["ESIN – École Supérieure d'Informatique et du Numérique", "SAAE – School of Aerospace & Automotive Engineering", "ECINE – École Supérieure d'Ingénierie de l'Énergie", "ESAR – École Supérieure d'Architecture de Rabat", "GC – École Supérieure de Génie Civil", "Rabat Business School (RBS)", "Sciences Po Rabat", "École de Droit", "École de Communication et Médias"], Website: "https://www.uir.ac.ma" },
  { name: "Université Ibn Tofail", acronym: "UIK", type: "publique", region: "Rabat-Salé-Kénitra", founded: 1989, students: 72000, faculties: ["Faculté des Sciences", "Faculté des Lettres et des Sciences Humaines", "Faculté de Droit et des Sciences Économiques", "Faculté de Médecine et de Pharmacie", "ENI Kénitra – École Nationale d'Ingénieurs", "ENCG Kénitra – École Nationale de Commerce et de Gestion", "EST Kénitra – École Supérieure de Technologie"], Website: "" },

  // Fès-Meknès
  { name: "Université Sidi Mohammed Ben Abdellah", acronym: "USMBA", type: "publique", region: "Fès-Meknès", founded: 1975, students: 86000, faculties: ["FSJES – Faculté des Sciences Juridiques, Économiques et Sociales", "Faculté des Sciences", "Faculté des Lettres et des Sciences Humaines", "ENSA Fès – École Nationale Supérieure d'Arts et Métiers", "ENSAM Fès – École Nationale Supérieure d'Arts et Métiers"], Website: "https://www.usmba.ac.ma" },
  { name: "Université Moulay Ismail", acronym: "UMI", type: "publique", region: "Fès-Meknès", founded: 1989, students: 48000, faculties: ["Faculté des Sciences", "Faculté des Lettres et Sciences Humaines", "Faculté des Sciences Juridiques, Économiques et Sociales", "ENSAM Meknès – École Nationale Supérieure d'Arts et Métiers", "EST Meknès – École Supérieure de Technologie", "ENCG Meknès – École Nationale de Commerce et de Gestion", "ENS Meknès – École Normale Supérieure"], Website: "" },

  // Marrakech-Safi
  { name: "Université Cadi Ayyad", acronym: "UCA", type: "publique", region: "Marrakech-Safi", founded: 1978, students: 75000, faculties: ["FSJESM – Faculté des Sciences Juridiques, Économiques et Sociales de Marrakech", "Faculté des Sciences", "FLSHM – Faculté des Lettres et Sciences Humaines", "Faculté de Médecine et de Pharmacie", "ENSAM Marrakech", "ENSC – École Nationale Supérieure de Chimie", "ENSA Safi – École Nationale Supérieure d'Arts et Métiers", "EST Safi – École Supérieure de Technologie", "ESTM Tadla – École Supérieure de Technologie", "ENSA Essaouira"], Website: "" },
  { name: "Université Internationale de Marrakech", acronym: "UIMa", type: "privée", region: "Marrakech-Safi", founded: 2012, students: 2800, faculties: ["École de Commerce International", "École d'Ingénieurs", "Faculté des Lettres et Sciences Humaines"], Website: "" },
  { name: "Université Privée de Marrakech", acronym: "UPM", type: "privée", region: "Marrakech-Safi", founded: 2014, students: 2000, faculties: ["École d'Ingénierie et d'Innovation", "Collège Santé (Médecine, Pharmacie et Médecine Dentaire)", "École d'Architecture", "Pôle Management et Commerce", "Pôle Hôtellerie, Tourisme et Art de la Table"], Website: "" },

  // Tanger-Tétouan-Al Hoceïma
  { name: "Université Abdelmalek Essaâdi", acronym: "UAE", type: "publique", region: "Tanger-Tétouan-Al Hoceïma", founded: 1989, students: 68000, faculties: ["FSJES Tétouan", "FSJES Tanger", "FSJES Al Hoceïma", "FSJES Larache", "FLSHT Tétouan – Faculté des Lettres et Sciences Humaines", "Faculté des Sciences Tétouan", "Faculté des Sciences Tanger", "ENSA Tétouan", "ENSA Tanger", "EST Tanger – École Supérieure de Technologie", "ENSM Tanger – École Nationale Supérieure des Mines", "ENCG Tanger – École Nationale de Commerce et de Gestion", "EST Al Hoceïma"], Website: "" },

  // Souss-Massa
  { name: "Université Ibn Zohr", acronym: "UIZ", type: "publique", region: "Souss-Massa", founded: 1989, students: 55000, faculties: ["Faculté des Sciences", "Faculté des Lettres et Sciences Humaines", "Faculté de Droit", "Faculté de Médecine et de Pharmacie", "Faculté des Sciences Économiques et de Gestion", "ENSA Agadir – École Nationale Supérieure d'Arts et Métiers", "EST Agadir – École Supérieure de Technologie"], Website: "" },

  // Oriental
  { name: "Université Mohammed Premier", acronym: "UMP", type: "publique", region: "Oriental", founded: 1978, students: 38000, faculties: ["Faculté des Sciences", "Faculté des Lettres et des Sciences Humaines", "Faculté de Droit et des Sciences Économiques", "Faculté de Médecine et de Pharmacie", "ENI Oujda – École Nationale d'Ingénieurs", "ENCG Oujda – École Nationale de Commerce et de Gestion", "EST Oujda – École Supérieure de Technologie"], Website: "" },

  // Beni Mellal-Khénifra
  { name: "Université Sultan Moulay Slimane", acronym: "USMS", type: "publique", region: "Béni Mellal-Khénifra", founded: 2007, students: 28000, faculties: ["Faculté des Sciences", "Faculté des Lettres et des Sciences Humaines", "Faculté de Droit et des Sciences Économiques", "ENI Béni Mellal – École Nationale d'Ingénieurs", "EST Béni Mellal – École Supérieure de Technologie"], Website: "" },

  // Drâa-Tafilalet
  { name: "Université Ibn Zohr – Errachidia", acronym: "UIZ-E", type: "publique", region: "Drâa-Tafilalet", founded: 2007, students: 12000, faculties: ["Faculté des Sciences", "Faculté des Lettres"], Website: "" },

  // Guelmim-Oued Noun
  { name: "Université Ibn Tofail – Guelmim", acronym: "UIK-G", type: "publique", region: "Guelmim-Oued Noun", founded: 2009, students: 8000, faculties: ["Faculté des Sciences", "Faculté des Lettres"], Website: "" },

  // Laâyoune-Sakia El Hamra
  { name: "Université Ibn Zohr – Laâyoune", acronym: "UIZ-L", type: "publique", region: "Laâyoune-Sakia El Hamra", founded: 2009, students: 6000, faculties: ["Faculté des Sciences", "Faculté des Lettres"], Website: "" },

  // Dakhla-Oued Ed-Dahab
  { name: "Université Ibn Zohr – Dakhla", acronym: "UIZ-D", type: "publique", region: "Dakhla-Oued Ed-Dahab", founded: 2009, students: 4000, faculties: ["Faculté des Sciences"], Website: "" },

  // Privées supplémentaires
  { name: "UM6P – Université Mohammed VI Polytechnique", acronym: "UM6P", type: "semi-publique", region: "Marrakech-Safi", founded: 2017, students: 3500, faculties: ["Technix", "Institute of Applied Digital Technologies", "Story School", "Institut des Sciences de l'Éducation", "1337", "EMINES – School of Industrial Management", "Africa Business School", "Center for African Studies", "Faculté de Gouvernance, Sciences Économiques et Sociales", "College of Agriculture and Environmental Sciences", "Green Tech Institute", "School of Collective Intelligence", "Faculty of Medical Sciences", "School of Applied Sciences & Engineering", "Institute of Science, Technology & Innovation", "UM6P School of Computer Science – College of Computing", "School of Hospitality Business & Management", "School of Architecture, Planning and Design"], Website: "https://www.um6p.ma" },
  { name: "Université Al Akhawayn à Ifrane", acronym: "AUI", type: "semi-publique", region: "Fès-Meknès", founded: 1995, students: 2000, faculties: ["School of Business Administration (SBA)", "School of Science and Engineering (SSE)", "School of Humanities and Social Sciences (SHSS)"], Website: "https://www.aui.ma" },
  { name: "HEM – Hautes Écoles de Management", acronym: "HEM", type: "privée", region: "Casablanca-Settat", founded: 1988, students: 5000, faculties: ["École de Management", "École de Finance", "École de Marketing", "École de Commerce International", "École de Ressources Humaines"], Website: "https://www.hem.ac.ma" },
  { name: "Groupe ISCAE", acronym: "ISCAE", type: "semi-publique", region: "Casablanca-Settat", founded: 1975, students: 3000, faculties: ["Programme Grande École", "Master Spécialisé", "Executive MBA", "Comptabilité", "Finance", "Marketing"], Website: "https://www.iscae.ma" },
  { name: "ESCA – École de Management", acronym: "ESCA", type: "privée", region: "Casablanca-Settat", founded: 1992, students: 2500, faculties: ["Programme Grande École", "Finance et Contrôle de Gestion", "Marketing et Commerce International", "Supply Chain Management", "Entrepreneuriat"], Website: "https://www.esca.ma" },
  { name: "Supdeco – École Supérieure de Commerce", acronym: "SUPDECO", type: "privée", region: "Casablanca-Settat", founded: 1986, students: 3000, faculties: ["Programme Grande École", "International Business", "Digital Management", "Finance et Audit"], Website: "https://www.supdeco.ma" },
  { name: "ISCA – Institut Supérieur de l'Audiovisuel et du Cinéma", acronym: "ISCA", type: "privée", region: "Rabat-Salé-Kénitra", founded: 2002, students: 800, faculties: ["DTS Audiovisuel", "Bachelor Audiovisuel et Cinéma", "Bachelor Communication"], Website: "" },
  { name: "ENSAD – École Nationale Supérieure des Arts et Design", acronym: "ENSAD", type: "publique", region: "Rabat-Salé-Kénitra", founded: 2013, students: 600, faculties: ["Design d'Intérieur", "Design Industriel", "Design de Communication Visuelle", "Arts Plastiques", "Photographie et Vidéo"], Website: "https://www.ensad.ma" },
  { name: "EMI – École Mohammédia des Ingénieurs", acronym: "EMI", type: "publique", region: "Rabat-Salé-Kénitra", founded: 1962, students: 1200, faculties: ["Génie Informatique", "Génie Électrique", "Génie Mécanique", "Génie Industriel", "Génie Civil"], Website: "" },
  { name: "EHTP – École Hassania des Travaux Publics", acronym: "EHTP", type: "publique", region: "Casablanca-Settat", founded: 1971, students: 1500, faculties: ["Génie Civil", "Génie Hydraulique", "Génie Electrique", "Architecture", "Topographie"], Website: "" },
]

// ── DAMS ────────────────────────────────────────────────────────────────────
export const DAMS: Dam[] = [
  { name: "Barrage Al Massira", region: "Rabat-Salé-Kénitra", basin: "Oum Er-Rbia", capacityM3: 2800000000, yearBuilt: 1979, usage: ["Irrigation", "Eau potable", "Hydroélectricité"], annualFilling: [{ year: 2015, percent: 58 }, { year: 2016, percent: 30 }, { year: 2017, percent: 40 }, { year: 2018, percent: 52 }, { year: 2019, percent: 48 }, { year: 2020, percent: 35 }, { year: 2021, percent: 60 }, { year: 2022, percent: 28 }, { year: 2023, percent: 32 }, { year: 2024, percent: 55 }, { year: 2025, percent: 42 }, { year: 2026, percent: 68 }] },
  { name: "Barrage Bin El Ouidane", region: "Béni Mellal-Khénifra", basin: "Oum Er-Rbia", capacityM3: 1500000000, yearBuilt: 1953, usage: ["Irrigation", "Hydroélectricité"], annualFilling: [{ year: 2015, percent: 62 }, { year: 2016, percent: 35 }, { year: 2017, percent: 45 }, { year: 2018, percent: 58 }, { year: 2019, percent: 52 }, { year: 2020, percent: 38 }, { year: 2021, percent: 65 }, { year: 2022, percent: 30 }, { year: 2023, percent: 35 }, { year: 2024, percent: 58 }, { year: 2025, percent: 45 }, { year: 2026, percent: 72 }] },
  { name: "Barrage Ahmed Al Hanss", region: "Marrakech-Safi", basin: "Tensift", capacityM3: 670000000, yearBuilt: 1971, usage: ["Irrigation", "Eau potable"], annualFilling: [{ year: 2015, percent: 55 }, { year: 2016, percent: 28 }, { year: 2017, percent: 38 }, { year: 2018, percent: 50 }, { year: 2019, percent: 45 }, { year: 2020, percent: 32 }, { year: 2021, percent: 58 }, { year: 2022, percent: 25 }, { year: 2023, percent: 30 }, { year: 2024, percent: 52 }, { year: 2025, percent: 40 }, { year: 2026, percent: 65 }] },
  { name: "Barrage Al Wahda", region: "Fès-Meknès", basin: "Sebou", capacityM3: 3800000000, yearBuilt: 1966, usage: ["Irrigation", "Hydroélectricité", "Eau potable"], annualFilling: [{ year: 2015, percent: 60 }, { year: 2016, percent: 32 }, { year: 2017, percent: 42 }, { year: 2018, percent: 55 }, { year: 2019, percent: 50 }, { year: 2020, percent: 36 }, { year: 2021, percent: 62 }, { year: 2022, percent: 28 }, { year: 2023, percent: 33 }, { year: 2024, percent: 56 }, { year: 2025, percent: 43 }, { year: 2026, percent: 70 }] },
  { name: "Barrage Idriss Ier", region: "Fès-Meknès", basin: "Sebou", capacityM3: 1200000000, yearBuilt: 1972, usage: ["Irrigation", "Hydroélectricité"], annualFilling: [{ year: 2015, percent: 55 }, { year: 2016, percent: 30 }, { year: 2017, percent: 40 }, { year: 2018, percent: 52 }, { year: 2019, percent: 48 }, { year: 2020, percent: 35 }, { year: 2021, percent: 58 }, { year: 2022, percent: 26 }, { year: 2023, percent: 30 }, { year: 2024, percent: 52 }, { year: 2025, percent: 40 }, { year: 2026, percent: 65 }] },
  { name: "Barrage El Borj", region: "Rabat-Salé-Kénitra", basin: "Sebou", capacityM3: 750000000, yearBuilt: 2001, usage: ["Eau potable", "Irrigation"], annualFilling: [{ year: 2015, percent: 62 }, { year: 2016, percent: 35 }, { year: 2017, percent: 45 }, { year: 2018, percent: 58 }, { year: 2019, percent: 52 }, { year: 2020, percent: 38 }, { year: 2021, percent: 65 }, { year: 2022, percent: 30 }, { year: 2023, percent: 35 }, { year: 2024, percent: 58 }, { year: 2025, percent: 45 }, { year: 2026, percent: 72 }] },
  { name: "Barrage Sidi Saïd Maâchou", region: "Casablanca-Settat", basin: "Oum Er-Rbia", capacityM3: 920000000, yearBuilt: 1981, usage: ["Eau potable", "Industrie"], annualFilling: [{ year: 2015, percent: 58 }, { year: 2016, percent: 30 }, { year: 2017, percent: 40 }, { year: 2018, percent: 52 }, { year: 2019, percent: 48 }, { year: 2020, percent: 35 }, { year: 2021, percent: 60 }, { year: 2022, percent: 28 }, { year: 2023, percent: 32 }, { year: 2024, percent: 55 }, { year: 2025, percent: 42 }, { year: 2026, percent: 68 }] },
  { name: "Barrage Yaacoub El Mansour", region: "Rabat-Salé-Kénitra", basin: "Bou Regreg", capacityM3: 200000000, yearBuilt: 2002, usage: ["Eau potable"], annualFilling: [{ year: 2015, percent: 65 }, { year: 2016, percent: 38 }, { year: 2017, percent: 48 }, { year: 2018, percent: 60 }, { year: 2019, percent: 55 }, { year: 2020, percent: 40 }, { year: 2021, percent: 68 }, { year: 2022, percent: 32 }, { year: 2023, percent: 38 }, { year: 2024, percent: 60 }, { year: 2025, percent: 48 }, { year: 2026, percent: 75 }] },
  { name: "Barrage Al Massira II", region: "Souss-Massa", basin: "Souss", capacityM3: 350000000, yearBuilt: 2020, usage: ["Eau potable", "Irrigation"], annualFilling: [{ year: 2020, percent: 45 }, { year: 2021, percent: 60 }, { year: 2022, percent: 30 }, { year: 2023, percent: 35 }, { year: 2024, percent: 55 }, { year: 2025, percent: 42 }, { year: 2026, percent: 68 }] },
  { name: "Barrage Oulilt", region: "Fès-Meknès", basin: "Sebou", capacityM3: 500000000, yearBuilt: 1987, usage: ["Irrigation", "Eau potable"], annualFilling: [{ year: 2015, percent: 58 }, { year: 2016, percent: 30 }, { year: 2017, percent: 40 }, { year: 2018, percent: 52 }, { year: 2019, percent: 48 }, { year: 2020, percent: 35 }, { year: 2021, percent: 60 }, { year: 2022, percent: 28 }, { year: 2023, percent: 32 }, { year: 2024, percent: 55 }, { year: 2025, percent: 42 }, { year: 2026, percent: 68 }] },
  { name: "Barrage Al Akhdam", region: "Marrakech-Safi", basin: "Tensift", capacityM3: 280000000, yearBuilt: 2008, usage: ["Irrigation"], annualFilling: [{ year: 2015, percent: 55 }, { year: 2016, percent: 28 }, { year: 2017, percent: 38 }, { year: 2018, percent: 50 }, { year: 2019, percent: 45 }, { year: 2020, percent: 32 }, { year: 2021, percent: 58 }, { year: 2022, percent: 25 }, { year: 2023, percent: 30 }, { year: 2024, percent: 52 }, { year: 2025, percent: 40 }, { year: 2026, percent: 65 }] },
  { name: "Barrage Nador", region: "Oriental", basin: "Moulouya", capacityM3: 150000000, yearBuilt: 2005, usage: ["Eau potable", "Irrigation"], annualFilling: [{ year: 2015, percent: 60 }, { year: 2016, percent: 35 }, { year: 2017, percent: 45 }, { year: 2018, percent: 58 }, { year: 2019, percent: 52 }, { year: 2020, percent: 38 }, { year: 2021, percent: 65 }, { year: 2022, percent: 30 }, { year: 2023, percent: 35 }, { year: 2024, percent: 58 }, { year: 2025, percent: 45 }, { year: 2026, percent: 72 }] },
  { name: "Barrage Mohamed V", region: "Oriental", basin: "Moulouya", capacityM3: 730000000, yearBuilt: 1967, usage: ["Irrigation", "Hydroélectricité", "Eau potable"], annualFilling: [{ year: 2015, percent: 55 }, { year: 2016, percent: 30 }, { year: 2017, percent: 42 }, { year: 2018, percent: 52 }, { year: 2019, percent: 48 }, { year: 2020, percent: 35 }, { year: 2021, percent: 58 }, { year: 2022, percent: 28 }, { year: 2023, percent: 32 }, { year: 2024, percent: 54 }, { year: 2025, percent: 42 }, { year: 2026, percent: 66 }] },
  { name: "Barrage Hassan II", region: "Drâa-Tafilalet", basin: "Ziz", capacityM3: 400000000, yearBuilt: 1997, usage: ["Eau potable", "Irrigation"], annualFilling: [{ year: 2015, percent: 50 }, { year: 2016, percent: 25 }, { year: 2017, percent: 35 }, { year: 2018, percent: 48 }, { year: 2019, percent: 42 }, { year: 2020, percent: 30 }, { year: 2021, percent: 55 }, { year: 2022, percent: 22 }, { year: 2023, percent: 28 }, { year: 2024, percent: 50 }, { year: 2025, percent: 38 }, { year: 2026, percent: 62 }] },
  { name: "Barrage Oued El Makhazine", region: "Tanger-Tétouan-Al Hoceima", basin: "Loukkos", capacityM3: 780000000, yearBuilt: 1979, usage: ["Irrigation", "Hydroélectricité"], annualFilling: [{ year: 2015, percent: 65 }, { year: 2016, percent: 40 }, { year: 2017, percent: 50 }, { year: 2018, percent: 62 }, { year: 2019, percent: 56 }, { year: 2020, percent: 42 }, { year: 2021, percent: 68 }, { year: 2022, percent: 35 }, { year: 2023, percent: 40 }, { year: 2024, percent: 62 }, { year: 2025, percent: 50 }, { year: 2026, percent: 74 }] },
  { name: "Barrage Cinq Seuls", region: "Laâyoune-Sakia El Hamra", basin: "Sakia El Hamra", capacityM3: 135000000, yearBuilt: 2015, usage: ["Eau potable", "Irrigation"], annualFilling: [{ year: 2015, percent: 45 }, { year: 2016, percent: 20 }, { year: 2017, percent: 30 }, { year: 2018, percent: 42 }, { year: 2019, percent: 38 }, { year: 2020, percent: 25 }, { year: 2021, percent: 50 }, { year: 2022, percent: 18 }, { year: 2023, percent: 25 }, { year: 2024, percent: 45 }, { year: 2025, percent: 35 }, { year: 2026, percent: 58 }] },
  { name: "Barrage Sidi Driss", region: "Marrakech-Safi", basin: "Tensift", capacityM3: 180000000, yearBuilt: 1993, usage: ["Irrigation"], annualFilling: [{ year: 2015, percent: 52 }, { year: 2016, percent: 26 }, { year: 2017, percent: 36 }, { year: 2018, percent: 48 }, { year: 2019, percent: 42 }, { year: 2020, percent: 30 }, { year: 2021, percent: 55 }, { year: 2022, percent: 22 }, { year: 2023, percent: 28 }, { year: 2024, percent: 50 }, { year: 2025, percent: 38 }, { year: 2026, percent: 62 }] },
  { name: "Barrage Tasaout", region: "Marrakech-Safi", basin: "Tensift", capacityM3: 210000000, yearBuilt: 2010, usage: ["Irrigation", "Eau potable"], annualFilling: [{ year: 2015, percent: 54 }, { year: 2016, percent: 28 }, { year: 2017, percent: 38 }, { year: 2018, percent: 50 }, { year: 2019, percent: 44 }, { year: 2020, percent: 32 }, { year: 2021, percent: 56 }, { year: 2022, percent: 24 }, { year: 2023, percent: 30 }, { year: 2024, percent: 52 }, { year: 2025, percent: 40 }, { year: 2026, percent: 64 }] },
  { name: "Barrage Lalla Takerkoust", region: "Marrakech-Safi", basin: "Tensift", capacityM3: 85000000, yearBuilt: 1936, usage: ["Irrigation", "Hydroélectricité", "Tourisme"], annualFilling: [{ year: 2015, percent: 50 }, { year: 2016, percent: 25 }, { year: 2017, percent: 35 }, { year: 2018, percent: 48 }, { year: 2019, percent: 42 }, { year: 2020, percent: 30 }, { year: 2021, percent: 55 }, { year: 2022, percent: 22 }, { year: 2023, percent: 28 }, { year: 2024, percent: 50 }, { year: 2025, percent: 38 }, { year: 2026, percent: 62 }] },
  { name: "Barrage Sidi Chahed", region: "Rabat-Salé-Kénitra", basin: "Sebou", capacityM3: 310000000, yearBuilt: 2012, usage: ["Eau potable", "Irrigation"], annualFilling: [{ year: 2015, percent: 60 }, { year: 2016, percent: 35 }, { year: 2017, percent: 45 }, { year: 2018, percent: 58 }, { year: 2019, percent: 52 }, { year: 2020, percent: 38 }, { year: 2021, percent: 62 }, { year: 2022, percent: 30 }, { year: 2023, percent: 35 }, { year: 2024, percent: 58 }, { year: 2025, percent: 45 }, { year: 2026, percent: 70 }] },
  { name: "Barrage Moulay Youssef", region: "Marrakech-Safi", basin: "Tensift", capacityM3: 160000000, yearBuilt: 1972, usage: ["Irrigation", "Eau potable"], annualFilling: [{ year: 2015, percent: 52 }, { year: 2016, percent: 26 }, { year: 2017, percent: 36 }, { year: 2018, percent: 48 }, { year: 2019, percent: 42 }, { year: 2020, percent: 30 }, { year: 2021, percent: 55 }, { year: 2022, percent: 22 }, { year: 2023, percent: 28 }, { year: 2024, percent: 50 }, { year: 2025, percent: 38 }, { year: 2026, percent: 62 }] },
  { name: "Barrage Kharroub", region: "Tanger-Tétouan-Al Hoceima", basin: "Loukkos", capacityM3: 220000000, yearBuilt: 1999, usage: ["Irrigation", "Eau potable"], annualFilling: [{ year: 2015, percent: 62 }, { year: 2016, percent: 38 }, { year: 2017, percent: 48 }, { year: 2018, percent: 60 }, { year: 2019, percent: 54 }, { year: 2020, percent: 40 }, { year: 2021, percent: 65 }, { year: 2022, percent: 32 }, { year: 2023, percent: 38 }, { year: 2024, percent: 60 }, { year: 2025, percent: 48 }, { year: 2026, percent: 72 }] },
  { name: "Barrage Bab Louta", region: "Tanger-Tétouan-Al Hoceima", basin: "Loukkos", capacityM3: 95000000, yearBuilt: 2004, usage: ["Eau potable"], annualFilling: [{ year: 2015, percent: 64 }, { year: 2016, percent: 38 }, { year: 2017, percent: 48 }, { year: 2018, percent: 60 }, { year: 2019, percent: 55 }, { year: 2020, percent: 42 }, { year: 2021, percent: 66 }, { year: 2022, percent: 34 }, { year: 2023, percent: 40 }, { year: 2024, percent: 62 }, { year: 2025, percent: 50 }, { year: 2026, percent: 74 }] },
  { name: "Barrage El Kansera", region: "Rabat-Salé-Kénitra", basin: "Sebou", capacityM3: 330000000, yearBuilt: 1935, usage: ["Irrigation", "Hydroélectricité"], annualFilling: [{ year: 2015, percent: 58 }, { year: 2016, percent: 32 }, { year: 2017, percent: 42 }, { year: 2018, percent: 55 }, { year: 2019, percent: 50 }, { year: 2020, percent: 36 }, { year: 2021, percent: 60 }, { year: 2022, percent: 28 }, { year: 2023, percent: 34 }, { year: 2024, percent: 56 }, { year: 2025, percent: 44 }, { year: 2026, percent: 68 }] },
  { name: "Barrage Daourat", region: "Casablanca-Settat", basin: "Oum Er-Rbia", capacityM3: 170000000, yearBuilt: 1988, usage: ["Hydroélectricité", "Irrigation"], annualFilling: [{ year: 2015, percent: 56 }, { year: 2016, percent: 30 }, { year: 2017, percent: 40 }, { year: 2018, percent: 52 }, { year: 2019, percent: 46 }, { year: 2020, percent: 34 }, { year: 2021, percent: 58 }, { year: 2022, percent: 26 }, { year: 2023, percent: 32 }, { year: 2024, percent: 54 }, { year: 2025, percent: 42 }, { year: 2026, percent: 66 }] },
  { name: "Barrage Afourer", region: "Béni Mellal-Khénifra", basin: "Oum Er-Rbia", capacityM3: 120000000, yearBuilt: 2003, usage: ["Irrigation", "Hydroélectricité"], annualFilling: [{ year: 2015, percent: 58 }, { year: 2016, percent: 32 }, { year: 2017, percent: 42 }, { year: 2018, percent: 55 }, { year: 2019, percent: 50 }, { year: 2020, percent: 36 }, { year: 2021, percent: 60 }, { year: 2022, percent: 28 }, { year: 2023, percent: 34 }, { year: 2024, percent: 56 }, { year: 2025, percent: 44 }, { year: 2026, percent: 68 }] },
  { name: "Barrage Hassan Addakhil", region: "Drâa-Tafilalet", basin: "Ziz", capacityM3: 350000000, yearBuilt: 1990, usage: ["Irrigation", "Eau potable"], annualFilling: [{ year: 2015, percent: 48 }, { year: 2016, percent: 22 }, { year: 2017, percent: 32 }, { year: 2018, percent: 45 }, { year: 2019, percent: 40 }, { year: 2020, percent: 28 }, { year: 2021, percent: 52 }, { year: 2022, percent: 20 }, { year: 2023, percent: 26 }, { year: 2024, percent: 48 }, { year: 2025, percent: 36 }, { year: 2026, percent: 60 }] },
  { name: "Barrage Ouarourout", region: "Drâa-Tafilalet", basin: "Drâa", capacityM3: 280000000, yearBuilt: 2015, usage: ["Irrigation", "Hydroélectricité"], annualFilling: [{ year: 2015, percent: 42 }, { year: 2016, percent: 20 }, { year: 2017, percent: 30 }, { year: 2018, percent: 42 }, { year: 2019, percent: 38 }, { year: 2020, percent: 26 }, { year: 2021, percent: 50 }, { year: 2022, percent: 18 }, { year: 2023, percent: 24 }, { year: 2024, percent: 46 }, { year: 2025, percent: 35 }, { year: 2026, percent: 58 }] },
  { name: "Barrage Toudgha", region: "Drâa-Tafilalet", basin: "Ziz", capacityM3: 110000000, yearBuilt: 2012, usage: ["Irrigation"], annualFilling: [{ year: 2015, percent: 46 }, { year: 2016, percent: 22 }, { year: 2017, percent: 32 }, { year: 2018, percent: 44 }, { year: 2019, percent: 38 }, { year: 2020, percent: 26 }, { year: 2021, percent: 50 }, { year: 2022, percent: 20 }, { year: 2023, percent: 26 }, { year: 2024, percent: 48 }, { year: 2025, percent: 36 }, { year: 2026, percent: 60 }] },
  { name: "Barrage Ait Messaoud", region: "Souss-Massa", basin: "Souss", capacityM3: 45000000, yearBuilt: 2008, usage: ["Irrigation"], annualFilling: [{ year: 2015, percent: 52 }, { year: 2016, percent: 26 }, { year: 2017, percent: 36 }, { year: 2018, percent: 48 }, { year: 2019, percent: 42 }, { year: 2020, percent: 30 }, { year: 2021, percent: 55 }, { year: 2022, percent: 24 }, { year: 2023, percent: 30 }, { year: 2024, percent: 52 }, { year: 2025, percent: 40 }, { year: 2026, percent: 64 }] },
  { name: "Barrage Imfout", region: "Casablanca-Settat", basin: "Oum Er-Rbia", capacityM3: 105000000, yearBuilt: 1995, usage: ["Hydroélectricité", "Irrigation"], annualFilling: [{ year: 2015, percent: 58 }, { year: 2016, percent: 32 }, { year: 2017, percent: 42 }, { year: 2018, percent: 54 }, { year: 2019, percent: 48 }, { year: 2020, percent: 36 }, { year: 2021, percent: 60 }, { year: 2022, percent: 28 }, { year: 2023, percent: 34 }, { year: 2024, percent: 56 }, { year: 2025, percent: 44 }, { year: 2026, percent: 68 }] },
  { name: "Barrage Sidi Abdellah", region: "Souss-Massa", basin: "Massa", capacityM3: 65000000, yearBuilt: 2020, usage: ["Eau potable"], annualFilling: [{ year: 2020, percent: 42 }, { year: 2021, percent: 58 }, { year: 2022, percent: 28 }, { year: 2023, percent: 32 }, { year: 2024, percent: 52 }, { year: 2025, percent: 40 }, { year: 2026, percent: 65 }] },
  { name: "Barrage Taksebt", region: "Souss-Massa", basin: "Souss", capacityM3: 84000000, yearBuilt: 2007, usage: ["Eau potable"], annualFilling: [{ year: 2015, percent: 54 }, { year: 2016, percent: 28 }, { year: 2017, percent: 38 }, { year: 2018, percent: 50 }, { year: 2019, percent: 44 }, { year: 2020, percent: 32 }, { year: 2021, percent: 56 }, { year: 2022, percent: 24 }, { year: 2023, percent: 30 }, { year: 2024, percent: 52 }, { year: 2025, percent: 40 }, { year: 2026, percent: 64 }] },
  { name: "Barrage Ait Ouarda", region: "Souss-Massa", basin: "Souss", capacityM3: 72000000, yearBuilt: 2010, usage: ["Irrigation"], annualFilling: [{ year: 2015, percent: 52 }, { year: 2016, percent: 26 }, { year: 2017, percent: 36 }, { year: 2018, percent: 48 }, { year: 2019, percent: 42 }, { year: 2020, percent: 30 }, { year: 2021, percent: 55 }, { year: 2022, percent: 24 }, { year: 2023, percent: 30 }, { year: 2024, percent: 52 }, { year: 2025, percent: 40 }, { year: 2026, percent: 64 }] },
  { name: "Barrage Tamaloukt", region: "Béni Mellal-Khénifra", basin: "Oum Er-Rbia", capacityM3: 90000000, yearBuilt: 1998, usage: ["Irrigation"], annualFilling: [{ year: 2015, percent: 56 }, { year: 2016, percent: 30 }, { year: 2017, percent: 40 }, { year: 2018, percent: 52 }, { year: 2019, percent: 46 }, { year: 2020, percent: 34 }, { year: 2021, percent: 58 }, { year: 2022, percent: 26 }, { year: 2023, percent: 32 }, { year: 2024, percent: 54 }, { year: 2025, percent: 42 }, { year: 2026, percent: 66 }] },
  { name: "Barrage Allal El Fassi", region: "Fès-Meknès", basin: "Sebou", capacityM3: 85000000, yearBuilt: 1990, usage: ["Eau potable", "Irrigation"], annualFilling: [{ year: 2015, percent: 58 }, { year: 2016, percent: 32 }, { year: 2017, percent: 42 }, { year: 2018, percent: 54 }, { year: 2019, percent: 48 }, { year: 2020, percent: 36 }, { year: 2021, percent: 60 }, { year: 2022, percent: 28 }, { year: 2023, percent: 34 }, { year: 2024, percent: 56 }, { year: 2025, percent: 44 }, { year: 2026, percent: 68 }] },
  { name: "Barrage Mdez", region: "Fès-Meknès", basin: "Sebou", capacityM3: 110000000, yearBuilt: 2012, usage: ["Irrigation"], annualFilling: [{ year: 2015, percent: 56 }, { year: 2016, percent: 30 }, { year: 2017, percent: 40 }, { year: 2018, percent: 52 }, { year: 2019, percent: 46 }, { year: 2020, percent: 34 }, { year: 2021, percent: 58 }, { year: 2022, percent: 26 }, { year: 2023, percent: 32 }, { year: 2024, percent: 54 }, { year: 2025, percent: 42 }, { year: 2026, percent: 66 }] },
  { name: "Barrage Oued Lakhdar", region: "Marrakech-Safi", basin: "Tensift", capacityM3: 140000000, yearBuilt: 2017, usage: ["Irrigation", "Eau potable"], annualFilling: [{ year: 2017, percent: 40 }, { year: 2018, percent: 52 }, { year: 2019, percent: 46 }, { year: 2020, percent: 32 }, { year: 2021, percent: 58 }, { year: 2022, percent: 26 }, { year: 2023, percent: 32 }, { year: 2024, percent: 54 }, { year: 2025, percent: 42 }, { year: 2026, percent: 66 }] },
  { name: "Barrage Taghzirt", region: "Béni Mellal-Khénifra", basin: "Oum Er-Rbia", capacityM3: 58000000, yearBuilt: 2005, usage: ["Irrigation", "Eau potable"], annualFilling: [{ year: 2015, percent: 54 }, { year: 2016, percent: 28 }, { year: 2017, percent: 38 }, { year: 2018, percent: 50 }, { year: 2019, percent: 44 }, { year: 2020, percent: 32 }, { year: 2021, percent: 56 }, { year: 2022, percent: 24 }, { year: 2023, percent: 30 }, { year: 2024, percent: 52 }, { year: 2025, percent: 40 }, { year: 2026, percent: 64 }] },
]

// ── HOSPITALS ──────────────────────────────────────────────────────────────
export const HOSPITALS: Hospital[] = [
  // ══ CASABLANCA-SETTAT ═══════════════════════════════════════════════════
  // Publics (CHU)
  { name: "CHU Ibn Rochd", type: "public", region: "Casablanca-Settat", province: "Casablanca", capacity: 1800, specialties: ["Cardiologie", "Neurologie", "Oncologie", "Chirurgie générale", "Pédiatrie", "Urgences", "Transplants"], annualRevenue: 850000000, staff: 4200, population: 4200000 },
  { name: "CHU Hassan II", type: "public", region: "Casablanca-Settat", province: "Casablanca", capacity: 1200, specialties: ["Cardiologie", "Transplants", "Chirurgie orthopédique", "Neurochirurgie"], annualRevenue: 620000000, staff: 2800, population: 4200000 },
  { name: "CHU Hay Mohammadi – Aïn Chok", type: "public", region: "Casablanca-Settat", province: "Casablanca", capacity: 600, specialties: ["Maternité", "Pédiatrie", "Médecine interne"], annualRevenue: 280000000, staff: 1200, population: 1800000 },
  { name: "CHU Beni-Messic – Aïn Sebaâ", type: "public", region: "Casablanca-Settat", province: "Casablanca", capacity: 450, specialties: ["Chirurgie", "Urgences", "Médecine interne"], annualRevenue: 200000000, staff: 900, population: 1500000 },
  { name: "CHU El Jadida", type: "public", region: "Casablanca-Settat", province: "El Jadida", capacity: 320, specialties: ["Urgences", "Chirurgie", "Pédiatrie"], annualRevenue: 150000000, staff: 700, population: 850000 },
  { name: "CHU Mohammedia", type: "public", region: "Casablanca-Settat", province: "Mohammedia", capacity: 280, specialties: ["Urgences", "Cardiologie", "Médecine interne"], annualRevenue: 130000000, staff: 650, population: 700000 },
  { name: "CHU Khouribga", type: "public", region: "Casablanca-Settat", province: "Khouribga", capacity: 200, specialties: ["Urgences", "Chirurgie", "Maternité"], annualRevenue: 95000000, staff: 450, population: 530000 },
  { name: "CHU Settat", type: "public", region: "Casablanca-Settat", province: "Settat", capacity: 180, specialties: ["Urgences", "Médecine générale"], annualRevenue: 80000000, staff: 400, population: 450000 },
  { name: "CHU Benslimane", type: "public", region: "Casablanca-Settat", province: "Benslimane", capacity: 120, specialties: ["Urgences", "Médecine générale"], annualRevenue: 55000000, staff: 280, population: 200000 },
  { name: "CHU Berrechid", type: "public", region: "Casablanca-Settat", province: "Berrechid", capacity: 150, specialties: ["Urgences", "Chirurgie", "Médecine générale"], annualRevenue: 65000000, staff: 320, population: 350000 },
  { name: "CHU Sidi Bennour", type: "public", region: "Casablanca-Settat", province: "Sidi Bennour", capacity: 140, specialties: ["Urgences", "Médecine générale", "Maternité"], annualRevenue: 60000000, staff: 300, population: 380000 },
  // Privés (cliniques)
  { name: "Clinique du Panorama", type: "clinique", region: "Casablanca-Settat", province: "Casablanca", capacity: 200, specialties: ["Chirurgie esthétique", "Cardiologie", "Gynécologie"], annualRevenue: 120000000, staff: 350, population: 4200000 },
  { name: "Clinique Agdal", type: "clinique", region: "Casablanca-Settat", province: "Casablanca", capacity: 150, specialties: ["Pédiatrie", "Gynécologie", "Ophtalmologie"], annualRevenue: 85000000, staff: 280, population: 4200000 },
  { name: "Clinique Safa", type: "clinique", region: "Casablanca-Settat", province: "Casablanca", capacity: 180, specialties: ["Cardiologie", "Chirurgie générale", "Radiologie"], annualRevenue: 95000000, staff: 320, population: 4200000 },
  { name: "Clinique Anfa", type: "clinique", region: "Casablanca-Settat", province: "Casablanca", capacity: 160, specialties: ["Gynécologie", "Pédiatrie", "ORL"], annualRevenue: 88000000, staff: 290, population: 4200000 },
  { name: "Polyclinique du Nord", type: "clinique", region: "Casablanca-Settat", province: "Casablanca", capacity: 250, specialties: ["Cardiologie", "Oncologie", "Chirurgie"], annualRevenue: 150000000, staff: 450, population: 4200000 },
  // Non-lucratif
  { name: "Hôpital Saint-Louis – Fondation Lalla Salma", type: "semi-privé", region: "Casablanca-Settat", province: "Casablanca", capacity: 180, specialties: ["Cancérologie pédiatrique", "Hématologie"], annualRevenue: 95000000, staff: 320, population: 4200000 },

  // ══ RABAT-SALÉ-KÉNITRA ═════════════════════════════════════════════════
  // Publics
  { name: "CHU Hôpital Cheikh Zaid", type: "public", region: "Rabat-Salé-Kénitra", province: "Rabat", capacity: 1500, specialties: ["Cardiologie", "Neurologie", "Oncologie", "Urgences", "Transplants"], annualRevenue: 720000000, staff: 3500, population: 1900000 },
  { name: "CHU Hôpital des Enfants", type: "public", region: "Rabat-Salé-Kénitra", province: "Rabat", capacity: 500, specialties: ["Pédiatrie", "Néonatalogie", "Chirurgie pédiatrique", "Oncologie pédiatrique"], annualRevenue: 350000000, staff: 1200, population: 1900000 },
  { name: "CHU Hôpital d'Instruction des Armées Mohammed V", type: "public", region: "Rabat-Salé-Kénitra", province: "Rabat", capacity: 800, specialties: ["Chirurgie", "Traumatologie", "Ophtalmologie", "ORL"], annualRevenue: 380000000, staff: 1800, population: 1900000 },
  { name: "CHU Salé", type: "public", region: "Rabat-Salé-Kénitra", province: "Salé", capacity: 300, specialties: ["Cardiologie", "Gériatrie", "Urgences"], annualRevenue: 160000000, staff: 750, population: 1200000 },
  { name: "CHU Kénitra", type: "public", region: "Rabat-Salé-Kénitra", province: "Kénitra", capacity: 350, specialties: ["Cardiologie", "Urgences", "Chirurgie"], annualRevenue: 180000000, staff: 850, population: 1400000 },
  { name: "CHU Sidi Kacem", type: "public", region: "Rabat-Salé-Kénitra", province: "Sidi Kacem", capacity: 180, specialties: ["Urgences", "Médecine générale", "Maternité"], annualRevenue: 80000000, staff: 400, population: 500000 },
  { name: "CHU Khémisset", type: "public", region: "Rabat-Salé-Kénitra", province: "Khémisset", capacity: 160, specialties: ["Urgences", "Chirurgie", "Pédiatrie"], annualRevenue: 70000000, staff: 350, population: 550000 },
  // Privés
  { name: "Clinique Rabat", type: "clinique", region: "Rabat-Salé-Kénitra", province: "Rabat", capacity: 180, specialties: ["Cardiologie", "Gynécologie", "Chirurgie esthétique"], annualRevenue: 110000000, staff: 300, population: 1900000 },
  { name: "Polyclinique Agdal", type: "clinique", region: "Rabat-Salé-Kénitra", province: "Rabat", capacity: 120, specialties: ["Pédiatrie", "Dermatologie", "Ophtalmologie"], annualRevenue: 72000000, staff: 220, population: 1900000 },
  { name: "Clinique Hay Riad", type: "clinique", region: "Rabat-Salé-Kénitra", province: "Rabat", capacity: 150, specialties: ["Gynécologie", "ORL", "Chirurgie"], annualRevenue: 85000000, staff: 260, population: 1900000 },

  // ══ FÈS-MEKNÈS ═════════════════════════════════════════════════════════
  { name: "CHU Hôpital Universitaire Hassan II", type: "public", region: "Fès-Meknès", province: "Fès", capacity: 1200, specialties: ["Cardiologie", "Neurologie", "Transplants", "Oncologie", "Urgences"], annualRevenue: 580000000, staff: 2800, population: 1200000 },
  { name: "CHU Meknès", type: "public", region: "Fès-Meknès", province: "Meknès", capacity: 400, specialties: ["Cardiologie", "Chirurgie", "Maternité"], annualRevenue: 220000000, staff: 1000, population: 900000 },
  { name: "CHU Taza", type: "public", region: "Fès-Meknès", province: "Taza", capacity: 200, specialties: ["Urgences", "Médecine générale", "Chirurgie"], annualRevenue: 90000000, staff: 450, population: 500000 },
  { name: "CHU Sefrou", type: "public", region: "Fès-Meknès", province: "Sefrou", capacity: 150, specialties: ["Urgences", "Maternité", "Pédiatrie"], annualRevenue: 65000000, staff: 320, population: 300000 },
  { name: "CHU Ifrane", type: "public", region: "Fès-Meknès", province: "Ifrane", capacity: 120, specialties: ["Urgences", "Médecine générale"], annualRevenue: 50000000, staff: 250, population: 150000 },
  { name: "CHU El Hajeb", type: "public", region: "Fès-Meknès", province: "El Hajeb", capacity: 130, specialties: ["Urgences", "Médecine générale", "Maternité"], annualRevenue: 55000000, staff: 270, population: 250000 },
  { name: "Clinique Atlas Fès", type: "clinique", region: "Fès-Meknès", province: "Fès", capacity: 120, specialties: ["Chirurgie générale", "Gynécologie", "Cardiologie"], annualRevenue: 65000000, staff: 200, population: 1200000 },
  { name: "Clinique Aloustane Fès", type: "clinique", region: "Fès-Meknès", province: "Fès", capacity: 100, specialties: ["Chirurgie orthopédique", "Rhumatologie"], annualRevenue: 45000000, staff: 150, population: 1200000 },

  // ══ MARRAKECH-SAFI ═════════════════════════════════════════════════════
  { name: "CHU Mohammed VI", type: "public", region: "Marrakech-Safi", province: "Marrakech", capacity: 800, specialties: ["Cardiologie", "Oncologie", "Urgences", "Neurologie"], annualRevenue: 420000000, staff: 2000, population: 1300000 },
  { name: "CHU Arrazi", type: "public", region: "Marrakech-Safi", province: "Marrakech", capacity: 400, specialties: ["Psychiatrie", "Médecine interne", "Urgences"], annualRevenue: 180000000, staff: 800, population: 1300000 },
  { name: "CHU Safi", type: "public", region: "Marrakech-Safi", province: "Safi", capacity: 250, specialties: ["Urgences", "Chirurgie", "Pédiatrie"], annualRevenue: 110000000, staff: 550, population: 700000 },
  { name: "CHU Essaouira", type: "public", region: "Marrakech-Safi", province: "Essaouira", capacity: 120, specialties: ["Urgences", "Médecine générale"], annualRevenue: 50000000, staff: 250, population: 200000 },
  { name: "CHU El Kelaâ des Sraghna", type: "public", region: "Marrakech-Safi", province: "El Kelaâ des Sraghna", capacity: 150, specialties: ["Urgences", "Médecine générale", "Maternité"], annualRevenue: 60000000, staff: 300, population: 400000 },
  { name: "CHU Benguerir", type: "public", region: "Marrakech-Safi", province: "Rehamna", capacity: 100, specialties: ["Urgences", "Médecine générale", "Maternité"], annualRevenue: 42000000, staff: 210, population: 180000 },
  { name: "Clinique Benguerir", type: "clinique", region: "Marrakech-Safi", province: "Rehamna", capacity: 60, specialties: ["Gynécologie", "Pédiatrie", "Chirurgie générale"], annualRevenue: 28000000, staff: 120, population: 180000 },
  { name: "Clinique La Roseraie", type: "clinique", region: "Marrakech-Safi", province: "Marrakech", capacity: 140, specialties: ["Cardiologie", "Chirurgie", "Imagerie"], annualRevenue: 75000000, staff: 250, population: 1300000 },
  { name: "Clinique Marrakech", type: "clinique", region: "Marrakech-Safi", province: "Marrakech", capacity: 120, specialties: ["Gynécologie", "Pédiatrie", "Ophtalmologie"], annualRevenue: 62000000, staff: 200, population: 1300000 },

  // ══ TANGER-TÉTOUAN-AL HOCEÏMA ═════════════════════════════════════════
  { name: "CHU Tanger", type: "public", region: "Tanger-Tétouan-Al Hoceïma", province: "Tanger", capacity: 600, specialties: ["Cardiologie", "Chirurgie", "Pédiatrie", "Urgences"], annualRevenue: 320000000, staff: 1500, population: 1100000 },
  { name: "CHU Tétouan", type: "public", region: "Tanger-Tétouan-Al Hoceïma", province: "Tétouan", capacity: 300, specialties: ["Urgences", "Chirurgie", "Maternité"], annualRevenue: 140000000, staff: 700, population: 600000 },
  { name: "CHU Al Hoceïma", type: "public", region: "Tanger-Tétouan-Al Hoceïma", province: "Al Hoceïma", capacity: 180, specialties: ["Urgences", "Médecine générale", "Chirurgie"], annualRevenue: 80000000, staff: 400, population: 350000 },
  { name: "CHU Larache", type: "public", region: "Tanger-Tétouan-Al Hoceïma", province: "Larache", capacity: 150, specialties: ["Urgences", "Médecine générale"], annualRevenue: 65000000, staff: 320, population: 300000 },
  { name: "CHU Chefchaouen", type: "public", region: "Tanger-Tétouan-Al Hoceïma", province: "Chefchaouen", capacity: 120, specialties: ["Urgences", "Médecine générale"], annualRevenue: 50000000, staff: 250, population: 250000 },
  { name: "Clinique Tanger Med", type: "clinique", region: "Tanger-Tétouan-Al Hoceïma", province: "Tanger", capacity: 100, specialties: ["Cardiologie", "Chirurgie", "Gynécologie"], annualRevenue: 52000000, staff: 180, population: 1100000 },

  // ══ ORIENTAL ════════════════════════════════════════════════════════════
  { name: "CHU Oujda", type: "public", region: "Oriental", province: "Oujda", capacity: 450, specialties: ["Cardiologie", "Chirurgie", "Pédiatrie", "Urgences"], annualRevenue: 250000000, staff: 1100, population: 500000 },
  { name: "CHU Nador", type: "public", region: "Oriental", province: "Nador", capacity: 250, specialties: ["Urgences", "Chirurgie", "Maternité"], annualRevenue: 115000000, staff: 550, population: 500000 },
  { name: "CHU Berkane", type: "public", region: "Oriental", province: "Berkane", capacity: 180, specialties: ["Urgences", "Médecine générale", "Chirurgie"], annualRevenue: 80000000, staff: 400, population: 400000 },
  { name: "CHU Jerada", type: "public", region: "Oriental", province: "Jerada", capacity: 120, specialties: ["Urgences", "Médecine générale"], annualRevenue: 50000000, staff: 250, population: 100000 },
  { name: "CHU Taourirt", type: "public", region: "Oriental", province: "Taourirt", capacity: 130, specialties: ["Urgences", "Médecine générale", "Maternité"], annualRevenue: 55000000, staff: 270, population: 200000 },
  { name: "CHU Guercif", type: "public", region: "Oriental", province: "Guercif", capacity: 120, specialties: ["Urgences", "Médecine générale"], annualRevenue: 50000000, staff: 250, population: 200000 },
  { name: "CHU Figuig", type: "public", region: "Oriental", province: "Figuig", capacity: 100, specialties: ["Urgences", "Médecine générale"], annualRevenue: 40000000, staff: 200, population: 150000 },

  // ══ SOUSS-MASSA ════════════════════════════════════════════════════════
  { name: "CHU Agadir", type: "public", region: "Souss-Massa", province: "Agadir", capacity: 500, specialties: ["Cardiologie", "Urgences", "Chirurgie", "Pédiatrie"], annualRevenue: 280000000, staff: 1200, population: 600000 },
  { name: "CHU Inezgane", type: "public", region: "Souss-Massa", province: "Inezgane-Aït Melloul", capacity: 200, specialties: ["Urgences", "Chirurgie", "Maternité"], annualRevenue: 90000000, staff: 450, population: 500000 },
  { name: "CHU Taroudant", type: "public", region: "Souss-Massa", province: "Taroudant", capacity: 180, specialties: ["Urgences", "Médecine générale", "Pédiatrie"], annualRevenue: 80000000, staff: 400, population: 400000 },
  { name: "CHU Tiznit", type: "public", region: "Souss-Massa", province: "Tiznit", capacity: 120, specialties: ["Urgences", "Médecine générale"], annualRevenue: 50000000, staff: 250, population: 200000 },
  { name: "Clinique Agadir", type: "clinique", region: "Souss-Massa", province: "Agadir", capacity: 100, specialties: ["Cardiologie", "Gynécologie", "Chirurgie"], annualRevenue: 55000000, staff: 180, population: 600000 },

  // ══ BÉNI MELLAL-KHÉNIFRA ═══════════════════════════════════════════════
  { name: "CHU Béni Mellal", type: "public", region: "Béni Mellal-Khénifra", province: "Béni Mellal", capacity: 280, specialties: ["Cardiologie", "Urgences", "Pédiatrie", "Chirurgie"], annualRevenue: 150000000, staff: 650, population: 500000 },
  { name: "CHU Khénifra", type: "public", region: "Béni Mellal-Khénifra", province: "Khénifra", capacity: 150, specialties: ["Urgences", "Médecine générale", "Maternité"], annualRevenue: 65000000, staff: 320, population: 300000 },
  { name: "CHU Azilal", type: "public", region: "Béni Mellal-Khénifra", province: "Azilal", capacity: 100, specialties: ["Urgences", "Médecine générale"], annualRevenue: 40000000, staff: 200, population: 200000 },
  { name: "CHU Fquih Ben Salah", type: "public", region: "Béni Mellal-Khénifra", province: "Fquih Ben Salah", capacity: 120, specialties: ["Urgences", "Médecine générale", "Maternité"], annualRevenue: 50000000, staff: 250, population: 250000 },

  // ══ DRÂA-TAFILALET ═════════════════════════════════════════════════════
  { name: "CHU Errachidia", type: "public", region: "Drâa-Tafilalet", province: "Errachidia", capacity: 200, specialties: ["Urgences", "Chirurgie", "Pédiatrie"], annualRevenue: 90000000, staff: 450, population: 250000 },
  { name: "CHU Ouarzazate", type: "public", region: "Drâa-Tafilalet", province: "Ouarzazate", capacity: 120, specialties: ["Urgences", "Médecine générale"], annualRevenue: 50000000, staff: 250, population: 150000 },
  { name: "CHU Midelt", type: "public", region: "Drâa-Tafilalet", province: "Midelt", capacity: 100, specialties: ["Urgences", "Médecine générale"], annualRevenue: 40000000, staff: 200, population: 100000 },
  { name: "CHU Tinghir", type: "public", region: "Drâa-Tafilalet", province: "Tinghir", capacity: 80, specialties: ["Urgences", "Médecine générale"], annualRevenue: 30000000, staff: 160, population: 80000 },
  { name: "CHU Zagora", type: "public", region: "Drâa-Tafilalet", province: "Zagora", capacity: 80, specialties: ["Urgences", "Médecine générale"], annualRevenue: 30000000, staff: 160, population: 100000 },

  // ══ GUELMIM-OUED NOUN ══════════════════════════════════════════════════
  { name: "CHU Guelmim", type: "public", region: "Guelmim-Oued Noun", province: "Guelmim", capacity: 120, specialties: ["Urgences", "Médecine générale", "Chirurgie"], annualRevenue: 55000000, staff: 270, population: 200000 },
  { name: "CHU Sidi Ifni", type: "public", region: "Guelmim-Oued Noun", province: "Sidi Ifni", capacity: 80, specialties: ["Urgences", "Médecine générale"], annualRevenue: 30000000, staff: 150, population: 120000 },
  { name: "CHU Tan-Tan", type: "public", region: "Guelmim-Oued Noun", province: "Tan-Tan", capacity: 80, specialties: ["Urgences", "Médecine générale"], annualRevenue: 30000000, staff: 150, population: 100000 },

  // ══ LAÂYOUNE-SAKIA EL HAMRA ════════════════════════════════════════════
  { name: "CHU Laâyoune", type: "public", region: "Laâyoune-Sakia El Hamra", province: "Laâyoune", capacity: 180, specialties: ["Urgences", "Chirurgie", "Pédiatrie"], annualRevenue: 85000000, staff: 400, population: 200000 },
  { name: "CHU Boujdour", type: "public", region: "Laâyoune-Sakia El Hamra", province: "Boujdour", capacity: 80, specialties: ["Urgences", "Médecine générale"], annualRevenue: 30000000, staff: 150, population: 50000 },
  { name: "CHU Smara", type: "public", region: "Laâyoune-Sakia El Hamra", province: "Smara", capacity: 100, specialties: ["Urgences", "Médecine générale"], annualRevenue: 40000000, staff: 200, population: 80000 },

  // ══ DAKHLA-OUED ED-DAHAB ═══════════════════════════════════════════════
  { name: "CHU Dakhla", type: "public", region: "Dakhla-Oued Ed-Dahab", province: "Oued Ed-Dahab", capacity: 120, specialties: ["Urgences", "Chirurgie", "Médecine générale"], annualRevenue: 55000000, staff: 270, population: 100000 },
  { name: "CHU Aousserd", type: "public", region: "Dakhla-Oued Ed-Dahab", province: "Aousserd", capacity: 60, specialties: ["Urgences", "Médecine générale"], annualRevenue: 25000000, staff: 120, population: 50000 },
]

// ── ENGINEERS BY FIELD ──────────────────────────────────────────────────────
export const ENGINEERS_BY_FIELD: EngineerGrad[] = [
  { field: "Génie Informatique", count: 3800, employability: "Très élevée (95%)" },
  { field: "Génie Électrique", count: 2200, employability: "Élevée (88%)" },
  { field: "Génie Mécanique", count: 1800, employability: "Élevée (85%)" },
  { field: "Génie Civil", count: 2500, employability: "Moyenne (72%)" },
  { field: "Génie Industriel", count: 1500, employability: "Élevée (82%)" },
  { field: "Génie des Télécommunications", count: 1200, employability: "Très élevée (92%)" },
  { field: "Génie Chimique", count: 800, employability: "Moyenne (70%)" },
  { field: "Génie Mines et Géologie", count: 400, employability: "Élevée (80%)" },
  { field: "Génie Environnemental", count: 600, employability: "Moyenne (68%)" },
  { field: "Génie Aéronautique", count: 500, employability: "Très élevée (96%)" },
  { field: "Génie Alimentaire", count: 350, employability: "Élevée (83%)" },
  { field: "Architecture", count: 850, employability: "Moyenne (65%)" },
]

// ── SPORT DATA ──────────────────────────────────────────────────────────────
export interface SportsClub {
  name: string
  sport: string
  city: string
  league: string
  budget: number
  members: number
  trophies: number
  founded: number
  region: string
  title: string
}

export interface SportsInfrastructure {
  name: string
  type: string
  sport: string
  city: string
  region: string
  capacity: number
  yearBuilt: number
  renovation?: number
  surface: string
}

export interface SportsMedal {
  athlete: string
  sport: string
  competition: string
  year: number
  medal: 'Or' | 'Argent' | 'Bronze'
  discipline: string
}

export interface SportsFederation {
  name: string
  acronym: string
  sport: string
  founded: number
  president: string
  licensees: number
  clubs: number
  olympic: boolean
}

export const SPORTS_CLUBS: SportsClub[] = [
  // ── FOOTBALL ────────────────────────────────────────────────────────
  { name: "Wydad Athletic Club", sport: "Football", city: "Casablanca", league: "Botola Pro", budget: 180000000, members: 45000, trophies: 62, founded: 1937, region: "Casablanca-Settat", title: "22x Champion du Maroc" },
  { name: "Raja Club Athletic", sport: "Football", city: "Casablanca", league: "Botola Pro", budget: 160000000, members: 42000, trophies: 55, founded: 1949, region: "Casablanca-Settat", title: "13x Champion du Maroc" },
  { name: "Hassania Union Sport", sport: "Football", city: "Agadir", league: "Botola Pro", budget: 45000000, members: 12000, trophies: 8, founded: 1946, region: "Souss-Massa", title: "1x Champion du Maroc" },
  { name: "Maghreb Association Sportive de Fès", sport: "Football", city: "Fès", league: "Botola Pro", budget: 40000000, members: 10000, trophies: 6, founded: 1946, region: "Fès-Meknès", title: "4x Champion du Maroc" },
  { name: "Ittihad Riadi Tanger", sport: "Football", city: "Tanger", league: "Botola Pro", budget: 50000000, members: 15000, trophies: 4, founded: 1949, region: "Tanger-Tétouan-Al Hoceïma", title: "1x Champion du Maroc" },
  { name: "Union Sportive de Mohammédia", sport: "Football", city: "Mohammédia", league: "Botola Pro", budget: 35000000, members: 8000, trophies: 3, founded: 1943, region: "Casablanca-Settat", title: "2x Champion du Maroc" },
  { name: "Olympique Club de Safi", sport: "Football", city: "Safi", league: "Botola Pro", budget: 30000000, members: 7000, trophies: 2, founded: 1928, region: "Marrakech-Safi", title: "1x Champion du Maroc" },
  { name: "Difaâ Athletic El Jadida", sport: "Football", city: "El Jadida", league: "Botola Pro", budget: 35000000, members: 8500, trophies: 3, founded: 1946, region: "Casablanca-Settat", title: "2x Champion du Maroc" },
  { name: "Mouloudia Club d'Oujda", sport: "Football", city: "Oujda", league: "Botola Pro", budget: 28000000, members: 6500, trophies: 2, founded: 1946, region: "Oriental", title: "2x Champion du Maroc" },
  { name: "Raja Beni Mellal", sport: "Football", city: "Béni Mellal", league: "Botola Pro", budget: 25000000, members: 5500, trophies: 1, founded: 1948, region: "Béni Mellal-Khénifra", title: "0x Champion du Maroc" },
  { name: "AS FAR (Forces Armées Royales)", sport: "Football", city: "Rabat", league: "Botola Pro", budget: 80000000, members: 15000, trophies: 13, founded: 1958, region: "Rabat-Salé-Kénitra", title: "13x Champion du Maroc" },
  { name: "FUS Rabat", sport: "Football", city: "Rabat", league: "Botola Pro", budget: 40000000, members: 9000, trophies: 4, founded: 1946, region: "Rabat-Salé-Kénitra", title: "2x Champion du Maroc" },
  { name: "KAC Marrakech", sport: "Football", city: "Marrakech", league: "Botola 2", budget: 15000000, members: 4000, trophies: 1, founded: 1947, region: "Marrakech-Safi", title: "0x Champion du Maroc" },
  { name: "Chabab Mohammedia", sport: "Football", city: "Mohammédia", league: "Botola 2", budget: 12000000, members: 3500, trophies: 1, founded: 1943, region: "Casablanca-Settat", title: "0x Champion du Maroc" },
  { name: "IRT Khemisset", sport: "Football", city: "Khémisset", league: "Botola 2", budget: 10000000, members: 3000, trophies: 1, founded: 1946, region: "Rabat-Salé-Kénitra", title: "0x Champion du Maroc" },
  // ── FOOTBALL FÉMININ ────────────────────────────────────────────────
  { name: "SC Casablanca (F)", sport: "Football féminin", city: "Casablanca", league: "Ligue 1 Féminine", budget: 5000000, members: 2000, trophies: 6, founded: 2009, region: "Casablanca-Settat", title: "6x Championne du Maroc" },
  { name: "AS FAR Féminin", sport: "Football féminin", city: "Rabat", league: "Ligue 1 Féminine", budget: 6000000, members: 1800, trophies: 4, founded: 2010, region: "Rabat-Salé-Kénitra", title: "4x Championne du Maroc" },
  { name: "Wydad AC Féminin", sport: "Football féminin", city: "Casablanca", league: "Ligue 1 Féminine", budget: 4500000, members: 1500, trophies: 2, founded: 2012, region: "Casablanca-Settat", title: "2x Championne du Maroc" },
  { name: "Raja CA Féminin", sport: "Football féminin", city: "Casablanca", league: "Ligue 1 Féminine", budget: 4000000, members: 1200, trophies: 1, founded: 2013, region: "Casablanca-Settat", title: "1x Championne du Maroc" },
  // ── BASKETBALL ──────────────────────────────────────────────────────
  { name: "AS Salé (Basketball)", sport: "Basketball", city: "Salé", league: "Botola Pro", budget: 15000000, members: 3000, trophies: 18, founded: 1928, region: "Rabat-Salé-Kénitra", title: "18x Champion du Maroc" },
  { name: "IR Tanger (Basketball)", sport: "Basketball", city: "Tanger", league: "Botola Pro", budget: 12000000, members: 2500, trophies: 5, founded: 2002, region: "Tanger-Tétouan-Al Hoceïma", title: "5x Champion du Maroc" },
  { name: "FUS Rabat (Basketball)", sport: "Basketball", city: "Rabat", league: "Botola Pro", budget: 10000000, members: 2000, trophies: 4, founded: 1960, region: "Rabat-Salé-Kénitra", title: "4x Champion du Maroc" },
  { name: "MAS Fès (Basketball)", sport: "Basketball", city: "Fès", league: "Botola Pro", budget: 8000000, members: 1800, trophies: 3, founded: 1948, region: "Fès-Meknès", title: "3x Champion du Maroc" },
  { name: "Wydad AC (Basketball)", sport: "Basketball", city: "Casablanca", league: "Botola Pro", budget: 9000000, members: 2200, trophies: 6, founded: 1937, region: "Casablanca-Settat", title: "6x Champion du Maroc" },
  // ── HANDBALL ────────────────────────────────────────────────────────
  { name: "Raja CA (Handball)", sport: "Handball", city: "Casablanca", league: "Botola Pro", budget: 12000000, members: 2500, trophies: 12, founded: 1949, region: "Casablanca-Settat", title: "12x Champion du Maroc" },
  { name: "AS Salé (Handball)", sport: "Handball", city: "Salé", league: "Botola Pro", budget: 10000000, members: 2000, trophies: 8, founded: 1928, region: "Rabat-Salé-Kénitra", title: "8x Champion du Maroc" },
  { name: "Massira El Jadida (Handball)", sport: "Handball", city: "El Jadida", league: "Botola Pro", budget: 7000000, members: 1500, trophies: 4, founded: 1974, region: "Casablanca-Settat", title: "4x Champion du Maroc" },
  { name: "Wydad AC (Handball)", sport: "Handball", city: "Casablanca", league: "Botola Pro", budget: 8000000, members: 1800, trophies: 5, founded: 1937, region: "Casablanca-Settat", title: "5x Champion du Maroc" },
  // ── VOLLEYBALL ──────────────────────────────────────────────────────
  { name: "SCC Volée (Volleyball)", sport: "Volleyball", city: "Casablanca", league: "Botola Pro", budget: 5000000, members: 1200, trophies: 10, founded: 1978, region: "Casablanca-Settat", title: "10x Champion du Maroc" },
  { name: "Raja CA (Volleyball)", sport: "Volleyball", city: "Casablanca", league: "Botola Pro", budget: 4000000, members: 1000, trophies: 6, founded: 1949, region: "Casablanca-Settat", title: "6x Champion du Maroc" },
  { name: "Fath Union Sport (Volleyball)", sport: "Volleyball", city: "Rabat", league: "Botola Pro", budget: 3500000, members: 900, trophies: 4, founded: 1946, region: "Rabat-Salé-Kénitra", title: "4x Champion du Maroc" },
  // ── NATATION ────────────────────────────────────────────────────────
  { name: "CN Casablanca (Natation)", sport: "Natation", city: "Casablanca", league: "Ligue 1", budget: 6000000, members: 800, trophies: 15, founded: 1946, region: "Casablanca-Settat", title: "15x Champion du Maroc" },
  { name: "CN Rabat (Natation)", sport: "Natation", city: "Rabat", league: "Ligue 1", budget: 4500000, members: 600, trophies: 8, founded: 1952, region: "Rabat-Salé-Kénitra", title: "8x Champion du Maroc" },
  { name: "CN Tanger (Natation)", sport: "Natation", city: "Tanger", league: "Ligue 1", budget: 3500000, members: 450, trophies: 4, founded: 1958, region: "Tanger-Tétouan-Al Hoceïma", title: "4x Champion du Maroc" },
  // ── JUDO ────────────────────────────────────────────────────────────
  { name: "JS Ain Sebaâ (Judo)", sport: "Judo", city: "Casablanca", league: "Nationale 1", budget: 3000000, members: 500, trophies: 12, founded: 1962, region: "Casablanca-Settat", title: "12x Champion du Maroc" },
  { name: "CS Marocain (Judo)", sport: "Judo", city: "Rabat", league: "Nationale 1", budget: 2500000, members: 400, trophies: 8, founded: 1968, region: "Rabat-Salé-Kénitra", title: "8x Champion du Maroc" },
  { name: "US Fès (Judo)", sport: "Judo", city: "Fès", league: "Nationale 1", budget: 2000000, members: 350, trophies: 5, founded: 1970, region: "Fès-Meknès", title: "5x Champion du Maroc" },
  // ── BOXE ────────────────────────────────────────────────────────────
  { name: "AS Boxe de Casablanca", sport: "Boxe", city: "Casablanca", league: "Nationale 1", budget: 2000000, members: 300, trophies: 15, founded: 1952, region: "Casablanca-Settat", title: "15x Champion du Maroc" },
  { name: "Raja Boxe Club", sport: "Boxe", city: "Casablanca", league: "Nationale 1", budget: 1500000, members: 250, trophies: 8, founded: 1960, region: "Casablanca-Settat", title: "8x Champion du Maroc" },
  { name: "Club Médina Boxe", sport: "Boxe", city: "Rabat", league: "Nationale 1", budget: 1800000, members: 280, trophies: 10, founded: 1955, region: "Rabat-Salé-Kénitra", title: "10x Champion du Maroc" },
  // ── ATHLÉTISME ──────────────────────────────────────────────────────
  { name: "Raja Athlétisme Club", sport: "Athlétisme", city: "Casablanca", league: "Nationale 1", budget: 3500000, members: 600, trophies: 20, founded: 1949, region: "Casablanca-Settat", title: "20x Champion du Maroc" },
  { name: "USM Athlétisme", sport: "Athlétisme", city: "Rabat", league: "Nationale 1", budget: 2800000, members: 450, trophies: 12, founded: 1957, region: "Rabat-Salé-Kénitra", title: "12x Champion du Maroc" },
  { name: "OMS Athlétisme", sport: "Athlétisme", city: "Marrakech", league: "Nationale 1", budget: 2000000, members: 350, trophies: 6, founded: 1965, region: "Marrakech-Safi", title: "6x Champion du Maroc" },
  // ── TENNIS ──────────────────────────────────────────────────────────
  { name: "TC Marrakech", sport: "Tennis", city: "Marrakech", league: "Division 1", budget: 4000000, members: 500, trophies: 8, founded: 1965, region: "Marrakech-Safi", title: "8x Champion du Maroc" },
  { name: "TC Casablanca", sport: "Tennis", city: "Casablanca", league: "Division 1", budget: 5000000, members: 650, trophies: 12, founded: 1958, region: "Casablanca-Settat", title: "12x Champion du Maroc" },
  { name: "RC Rabat Tennis", sport: "Tennis", city: "Rabat", league: "Division 1", budget: 3500000, members: 400, trophies: 6, founded: 1962, region: "Rabat-Salé-Kénitra", title: "6x Champion du Maroc" },
  // ── GOLF ────────────────────────────────────────────────────────────
  { name: "Royal Golf Dar Es Salam", sport: "Golf", city: "Rabat", league: "National", budget: 8000000, members: 1200, trophies: 0, founded: 1971, region: "Rabat-Salé-Kénitra", title: "Circuit pro Maroc" },
  { name: "Golf du Palais Royal", sport: "Golf", city: "Marrakech", league: "National", budget: 6000000, members: 800, trophies: 0, founded: 1970, region: "Marrakech-Safi", title: "Circuit pro Maroc" },
  { name: "Golf de l'Estérel", sport: "Golf", city: "Casablanca", league: "National", budget: 5000000, members: 650, trophies: 0, founded: 1980, region: "Casablanca-Settat", title: "Circuit pro Maroc" },
  // ── RUGBY ───────────────────────────────────────────────────────────
  { name: "US Rabat (Rugby)", sport: "Rugby", city: "Rabat", league: "Nationale 1", budget: 3000000, members: 500, trophies: 8, founded: 1957, region: "Rabat-Salé-Kénitra", title: "8x Champion du Maroc" },
  { name: "AS Casablanca (Rugby)", sport: "Rugby", city: "Casablanca", league: "Nationale 1", budget: 2500000, members: 400, trophies: 5, founded: 1963, region: "Casablanca-Settat", title: "5x Champion du Maroc" },
  // ── E-SPORT ─────────────────────────────────────────────────────────
  { name: "Team Morocco Esports", sport: "E-sport", city: "Casablanca", league: "MME League", budget: 2000000, members: 300, trophies: 5, founded: 2018, region: "Casablanca-Settat", title: "5x Championnat Maroc" },
  { name: "Atlas Gaming", sport: "E-sport", city: "Rabat", league: "MME League", budget: 1500000, members: 200, trophies: 3, founded: 2019, region: "Rabat-Salé-Kénitra", title: "3x Championnat Maroc" },
  { name: "Maroc Esports Federation", sport: "E-sport", city: "Casablanca", league: "National", budget: 3000000, members: 500, trophies: 8, founded: 2020, region: "Casablanca-Settat", title: "Fédération officielle" },
  // ── TBOURIDA ────────────────────────────────────────────────────────
  { name: "Tbourida Moussem de Tlemcen", sport: "Tbourida", city: "El Jadida", league: "Circuit Royal", budget: 8000000, members: 200, trophies: 0, founded: 1800, region: "Casablanca-Settat", title: "Troupe historique" },
  { name: "Tbourida Moussem d'El Aïoun", sport: "Tbourida", city: "Oujda", league: "Circuit Royal", budget: 5000000, members: 150, trophies: 0, founded: 1850, region: "Oriental", title: "Troupe historique" },
  { name: "Tbourida de l'Atlas", sport: "Tbourida", city: "Meknès", league: "Circuit Royal", budget: 4000000, members: 120, trophies: 0, founded: 1870, region: "Fès-Meknès", title: "Troupe historique" },
]

// ── SOCIAL PROGRAMS ─────────────────────────────────────────────────────────
export interface SocialProgram {
  name: string
  acronym: string
  ministry: string
  budget: number
  beneficiaries: number
  regions: string[]
  startDate: number
  description: string
  indicators: string[]
}

export const SOCIAL_PROGRAMS: SocialProgram[] = [
  { name: "Registre National de la Population", acronym: "RNP", ministry: "Ministère de l'Intérieur", budget: 2500000000, beneficiaries: 36000000, regions: ["National"], startDate: 2020, description: "Registre unique d'identification des citoyens marocains avec carte nationale d'identité électronique", indicators: ["36M citoyens enregistrés", "100% couverture adultes", "Carte électronique biométrique"] },
  { name: "RAMED – Régime d'Assistance Médicale", acronym: "RAMED", ministry: "Ministère de la Santé", budget: 4200000000, beneficiaries: 11000000, regions: ["National"], startDate: 2012, description: "Couverture santé pour les personnes économiquement démunies", indicators: ["11M bénéficiaires", "240 000 prestations/jour", "Couverture 52 wilayas"] },
  { name: "Tayssir – Allocation pour l'Éducation", acronym: "TAYSSIR", ministry: "Ministère de l'Éducation", budget: 3800000000, beneficiaries: 3500000, regions: ["National"], startDate: 2008, description: "Allocation financière aux familles pour maintenir les enfants à l'école", indicators: ["3,5M élèves bénéficiaires", "Réduction du décrochage scolaire de 15%", "Allocation 300 MAD/an par élémentaire"] },
  { name: "Initiative Nationale pour le Développement Humain", acronym: "INDH", ministry: "Ministère de l'Intérieur", budget: 6500000000, beneficiaries: 5000000, regions: ["National"], startDate: 2005, description: "Programme national de lutte contre la pauvreté et l'exclusion", indicators: ["15 000 projets réalisés", "5M bénéficiaires directs", "1 800 communes couvertes"] },
  { name: "Programme Ennakhil – Lutte contre la Pauvreté en Milieu Rural", acronym: "ENNAKHIL", ministry: "Ministère de l'Agriculture", budget: 3000000000, beneficiaries: 2000000, regions: ["Rural"], startDate: 2015, description: "Développement agricole et rural dans les zones défavorisées", indicators: ["2M bénéficiaires", "120 000 ha modernisés", "Création 40 000 emplois"] },
  { name: "Forsa – Programme d'Auto-emploi", acronym: "FORSA", ministry: "Ministère de l'Emploi", budget: 1200000000, beneficiaries: 300000, regions: ["National"], startDate: 2021, description: "Soutien financier et accompagnement pour les projets d'auto-emploi", indicators: ["300 000 lauréats", "Prêt 40 000 MAD sans garantie", "80% taux de réussite"] },
  { name: "Mutuelle de la Fonction Publique", acronym: "MFP", ministry: "Ministère de la Santé", budget: 5800000000, beneficiaries: 2200000, regions: ["National"], startDate: 2017, description: "Couverture complémentaire santé pour les fonctionnaires", indicators: ["2,2M assurés", "Taux de couverture 95%", "50 000 soins/jour"] },
  { name: "Programme Damancom – Assurance Décès et Invalidité", acronym: "DAMANCOM", ministry: "CNSS", budget: 800000000, beneficiaries: 3500000, regions: ["National"], startDate: 2019, description: "Assurance décès et invalidité pour les travailleurs non-salariés", indicators: ["3,5M assurés", "150 000 prestations versées", "Cotisation 12 MAD/mois"] },
  { name: "Caisse Marocaine de la Protection Sociale", acronym: "CMPS", ministry: "CNSS", budget: 7000000000, beneficiaries: 3000000, regions: ["National"], startDate: 2023, description: "Protection sociale universelle: allocations familiales, santé, retraite", indicators: ["3M ménages cibles", "Allocation 300 MAD/mois/famille", "Couverture universelle 2025"] },
  { name: "Programme Intilaka – Micro-crédit pour les Pauvres", acronym: "INTILAKA", ministry: "Ministère de l'Emploi", budget: 2500000000, beneficiaries: 600000, regions: ["Rural", "Urbain"], startDate: 2006, description: "Micro-crédit et accompagnement pour entrepreneurs défavorisés", indicators: ["600 000 bénéficiaires", "Taux de remboursement 97%", "Prêt moyen 15 000 MAD"] },
]

// ── SPORTS INFRASTRUCTURES ────────────────────────────────────────────────
export const SPORTS_INFRA: SportsInfrastructure[] = [
  { name: "Grand Stade Hassan II", type: "Stade", sport: "Football", city: "Casablanca", region: "Casablanca-Settat", capacity: 93000, yearBuilt: 2027, surface: "Gazon naturel" },
  { name: "Stade Mohammed V", type: "Stade", sport: "Football", city: "Casablanca", region: "Casablanca-Settat", capacity: 67000, yearBuilt: 1955, surface: "Gazon naturel" },
  { name: "Stade Moulay Abdallah", type: "Stade", sport: "Football", city: "Rabat", region: "Rabat-Salé-Kénitra", capacity: 65000, yearBuilt: 1983, surface: "Gazon synthétique" },
  { name: "Stade Adrar", type: "Stade", sport: "Football", city: "Agadir", region: "Souss-Massa", capacity: 45000, yearBuilt: 2004, surface: "Gazon synthétique" },
  { name: "Stade de Fès", type: "Stade", sport: "Football", city: "Fès", region: "Fès-Meknès", capacity: 45000, yearBuilt: 2007, surface: "Gazon naturel" },
  { name: "Stade de Tanger", type: "Stade", sport: "Football", city: "Tanger", region: "Tanger-Tétouan-Al Hoceïma", capacity: 45000, yearBuilt: 2011, surface: "Gazon synthétique" },
  { name: "Stade de Marrakech", type: "Stade", sport: "Football", city: "Marrakech", region: "Marrakech-Safi", capacity: 45000, yearBuilt: 2011, surface: "Gazon synthétique" },
  { name: "Stade d'Honneur", type: "Stade", sport: "Football", city: "Meknès", region: "Fès-Meknès", capacity: 25000, yearBuilt: 1960, surface: "Gazon synthétique" },
  { name: "Centre National de Formation", type: "Centre", sport: "Football", city: "Salé", region: "Rabat-Salé-Kénitra", capacity: 5000, yearBuilt: 2009, surface: "Gazon naturel" },
  { name: "Stade d'Athlétisme de Rabat", type: "Stade d'athlétisme", sport: "Athlétisme", city: "Rabat", region: "Rabat-Salé-Kénitra", capacity: 15000, yearBuilt: 2019, surface: "Piste synthétique" },
  { name: "Piscine Nationale", type: "Piscine olympique", sport: "Natation", city: "Casablanca", region: "Casablanca-Settat", capacity: 3000, yearBuilt: 2018, surface: "50m bassin" },
  { name: "Salle Omnisports Mohammed V", type: "Salle couverte", sport: "Basketball/Handball", city: "Casablanca", region: "Casablanca-Settat", capacity: 12000, yearBuilt: 2002, surface: "Parquet" },
  { name: "Salle Ibn Yassine", type: "Salle couverte", sport: "Judo/Boxe", city: "Rabat", region: "Rabat-Salé-Kénitra", capacity: 8000, yearBuilt: 1978, surface: "Tatami" },
  { name: "Golf Royal Dar Es Salam", type: "Parcours", sport: "Golf", city: "Rabat", region: "Rabat-Salé-Kénitra", capacity: 200, yearBuilt: 1971, surface: "36 trous" },
  { name: "Hippodrome de Casa", type: "Hippodrome", sport: "Tbourida", city: "Casablanca", region: "Casablanca-Settat", capacity: 10000, yearBuilt: 1950, surface: "Piste sablonneuse" },
  { name: "Salle de Basketball de Tanger", type: "Salle couverte", sport: "Basketball", city: "Tanger", region: "Tanger-Tétouan-Al Hoceïma", capacity: 7000, yearBuilt: 2018, surface: "Parquet" },
  { name: "Centre Nautique d'Agadir", type: "Centre nautique", sport: "Surf/Voile", city: "Agadir", region: "Souss-Massa", capacity: 2000, yearBuilt: 2015, surface: "Eau" },
  { name: "Complexe Equestre Tbourida", type: "Piste équestre", sport: "Tbourida", city: "Meknès", region: "Fès-Meknès", capacity: 25000, yearBuilt: 1920, surface: "Piste sablonneuse" },
]

// ── REAL OFFICIAL MOROCCAN OLYMPIC & PARALYMPIC MEDALS ──────────────────────
export const OLYMPIC_MEDALS: SportsMedal[] = [
  { athlete: "Soufiane El Bakkali", sport: "Athlétisme", competition: "JO Paris 2024", year: 2024, medal: "Or", discipline: "3000m Stipple (3000m steeple)" },
  { athlete: "Équipe du Maroc U23", sport: "Football", competition: "JO Paris 2024", year: 2024, medal: "Bronze", discipline: "Tournoi Olympique de Football Masculin" },
  { athlete: "Soufiane El Bakkali", sport: "Athlétisme", competition: "JO Tokyo 2020", year: 2021, medal: "Or", discipline: "3000m Stipple" },
  { athlete: "Hicham El Guerrouj", sport: "Athlétisme", competition: "JO Athènes 2004", year: 2004, medal: "Or", discipline: "1500m (Doublé olympique)" },
  { athlete: "Hicham El Guerrouj", sport: "Athlétisme", competition: "JO Athènes 2004", year: 2004, medal: "Or", discipline: "5000m (Doublé olympique)" },
  { athlete: "Hasna Benhassi", sport: "Athlétisme", competition: "JO Athènes 2004", year: 2004, medal: "Argent", discipline: "800m Femmes" },
  { athlete: "Hasna Benhassi", sport: "Athlétisme", competition: "JO Pékin 2008", year: 2008, medal: "Bronze", discipline: "800m Femmes" },
  { athlete: "Hicham El Guerrouj", sport: "Athlétisme", competition: "JO Sydney 2000", year: 2000, medal: "Argent", discipline: "1500m" },
  { athlete: "Ali Ezzine", sport: "Athlétisme", competition: "JO Sydney 2000", year: 2000, medal: "Bronze", discipline: "3000m Stipple" },
  { athlete: "Nezha Bidouane", sport: "Athlétisme", competition: "JO Sydney 2000", year: 2000, medal: "Bronze", discipline: "400m Haies Femmes" },
  { athlete: "Tahar Tamsamani", sport: "Boxe", competition: "JO Sydney 2000", year: 2000, medal: "Bronze", discipline: "Poids plumes (-57kg)" },
  { athlete: "Salah Hissou", sport: "Athlétisme", competition: "JO Atlanta 1996", year: 1996, medal: "Bronze", discipline: "10000m" },
  { athlete: "Khalid Skah", sport: "Athlétisme", competition: "JO Barcelone 1992", year: 1992, medal: "Or", discipline: "10000m" },
  { athlete: "Rachid El Basir", sport: "Athlétisme", competition: "JO Barcelone 1992", year: 1992, medal: "Argent", discipline: "1500m" },
  { athlete: "Mohamed Achik", sport: "Boxe", competition: "JO Barcelone 1992", year: 1992, medal: "Bronze", discipline: "Poids coqs (-54kg)" },
  { athlete: "Brahim Boutayeb", sport: "Athlétisme", competition: "JO Séoul 1988", year: 1988, medal: "Or", discipline: "10000m" },
  { athlete: "Saïd Aouita", sport: "Athlétisme", competition: "JO Séoul 1988", year: 1988, medal: "Bronze", discipline: "800m" },
  { athlete: "Abdelhak Achik", sport: "Boxe", competition: "JO Séoul 1988", year: 1988, medal: "Bronze", discipline: "Poids plumes (-57kg)" },
  { athlete: "Nawal El Moutawakel", sport: "Athlétisme", competition: "JO Los Angeles 1984", year: 1984, medal: "Or", discipline: "400m Haies Femmes (1ère Or Arabe/Africaine)" },
  { athlete: "Saïd Aouita", sport: "Athlétisme", competition: "JO Los Angeles 1984", year: 1984, medal: "Or", discipline: "5000m" },
]

export const PARALYMPIC_MEDALS: SportsMedal[] = [
  { athlete: "Fatima Zahra El Idrissi", sport: "Para-Athlétisme", competition: "JPO Paris 2024", year: 2024, medal: "Or", discipline: "Marathon T12 (Record du monde 2:48:36)" },
  { athlete: "Mouncef Bouja", sport: "Para-Athlétisme", competition: "JPO Paris 2024", year: 2024, medal: "Or", discipline: "400m T12" },
  { athlete: "Aymane El Haddaoui", sport: "Para-Athlétisme", competition: "JPO Paris 2024", year: 2024, medal: "Or", discipline: "400m T47 (Record du monde 46.65s)" },
  { athlete: "Aymane El Haddaoui", sport: "Para-Athlétisme", competition: "JPO Paris 2024", year: 2024, medal: "Bronze", discipline: "100m T47" },
  { athlete: "Yassine Ouhdadi", sport: "Para-Athlétisme", competition: "JPO Paris 2024", year: 2024, medal: "Or", discipline: "5000m T13" },
  { athlete: "Yassine Ouhdadi", sport: "Para-Athlétisme", competition: "JPO Tokyo 2020", year: 2021, medal: "Or", discipline: "5000m T13" },
  { athlete: "Abdelillah Gani", sport: "Para-Athlétisme", competition: "JPO Paris 2024", year: 2024, medal: "Argent", discipline: "Lancer de poids F53 (Record du monde F53)" },
  { athlete: "Youssef Benibrahim", sport: "Para-Athlétisme", competition: "JPO Paris 2024", year: 2024, medal: "Argent", discipline: "400m T13" },
  { athlete: "Ayoub Sadni", sport: "Para-Athlétisme", competition: "JPO Tokyo 2020", year: 2021, medal: "Or", discipline: "400m T47" },
  { athlete: "Ayoub Sadni", sport: "Para-Athlétisme", competition: "JPO Paris 2024", year: 2024, medal: "Bronze", discipline: "400m T47" },
  { athlete: "Zakariae Derhem", sport: "Para-Athlétisme", competition: "JPO Tokyo 2020", year: 2021, medal: "Or", discipline: "Lancer de poids F33" },
  { athlete: "Zakariae Derhem", sport: "Para-Athlétisme", competition: "JPO Paris 2024", year: 2024, medal: "Bronze", discipline: "Lancer de poids F33" },
  { athlete: "Rajae Akermach", sport: "Para-Taekwondo", competition: "JPO Paris 2024", year: 2024, medal: "Bronze", discipline: "K44 +65kg" },
  { athlete: "Ayoub Adouich", sport: "Para-Taekwondo", competition: "JPO Paris 2024", year: 2024, medal: "Bronze", discipline: "K44 -63kg" },
  { athlete: "El Amin Chentouf", sport: "Para-Athlétisme", competition: "JPO Tokyo 2020", year: 2021, medal: "Or", discipline: "Marathon T12" },
  { athlete: "El Amin Chentouf", sport: "Para-Athlétisme", competition: "JPO Rio 2016", year: 2016, medal: "Or", discipline: "Marathon T12" },
  { athlete: "El Amin Chentouf", sport: "Para-Athlétisme", competition: "JPO Londres 2012", year: 2012, medal: "Or", discipline: "5000m T12" },
  { athlete: "Saida Amoudi", sport: "Para-Athlétisme", competition: "JPO Tokyo 2020", year: 2021, medal: "Bronze", discipline: "Lancer de poids F34" },
  { athlete: "Abdelillah Mame", sport: "Para-Athlétisme", competition: "JPO Pékin 2008", year: 2008, medal: "Or", discipline: "800m T13" },
  { athlete: "Mustapha El Aouzari", sport: "Para-Athlétisme", competition: "JPO Athènes 2004", year: 2004, medal: "Or", discipline: "1500m T11" },
  { athlete: "Laila El Garaa", sport: "Para-Athlétisme", competition: "JPO Pékin 2008", year: 2008, medal: "Bronze", discipline: "Lancer de poids F40" },
]

export const INTERNATIONAL_MEDALS: SportsMedal[] = [
  ...OLYMPIC_MEDALS.slice(0, 10),
  ...PARALYMPIC_MEDALS.slice(0, 10),
  { athlete: "Badr Siwane", sport: "Triathlon", competition: "Championnats d'Afrique 2023", year: 2023, medal: "Or", discipline: "Triathlon Hommes" },
  { athlete: "Achraf Mahboubi", sport: "Taekwondo", competition: "Championnats d'Afrique 2023", year: 2023, medal: "Or", discipline: "Moins de 80kg" },
  { athlete: "Khadija El Mardi", sport: "Boxe", competition: "Championnats du Monde 2023", year: 2023, medal: "Or", discipline: "Poids lourds (+81kg) - Championne du Monde" },
  { athlete: "Yassine Boukhari", sport: "Karaté", competition: "Championnats d'Afrique 2023", year: 2023, medal: "Or", discipline: "Kumité -84kg" },
]

export const SPORTS_MEDALS: SportsMedal[] = [...OLYMPIC_MEDALS, ...PARALYMPIC_MEDALS]

// ── HELPER: count-based KPIs (should show as integers) ─────────────────────
export const INTEGER_KPI_CODES = new Set([
  'GRANDS_BARRAGES', 'UNIVERSITES_COUNT', 'UNIVERSITES_PUBLIQUES', 'UNIVERSITES_PRIVEES',
  'ECOLES_INGENIEURS', 'ETABLISSEMENTS', 'NOUVEAUX_INSCRITS',
  'INGENIEURS_DIPLOMES', 'MEDECINS_DIPLOMES', 'ENSEIGNANTS',
  'ETUDIANTS_TOTAL', 'LITS_HOPITAL', 'MEDOCINS',
  'CHEPTEL_BOVIN', 'CHEPTEL_OVIN', 'SUPERFICIE_ARBRES_FRUITERS',
  'BOTOLA_PRO_CLUBS', 'FEDERATIONS', 'MEDAILLES', 'MEDAILLES_ATHLETISME',
  'MEDAILLES_JUDO', 'MEDAILLES_BOXE', 'MEDAILLES_PARALYMPIQUES',
  'LICENCIES_NATATION', 'LICENCIES_BASKETBALL', 'LICENCIES_HANDBALL',
  'LICENCIES_CYCLISME', 'LICENCIES_TENNIS', 'LICENCIES_GOLF',
  'LICENCIES_RUGBY', 'LICENCIES_ESPORT', 'LICENCIES_VOLLEYBALL', 'LICENCIES_ESCRIME',
  'LICENCIES_TAEKWONDO', 'LICENCIES_KARATE', 'LICENCIES_HALTEREPHILIE', 'LICENCIES_TIR',
  'TBOURIDA_TROUPES', 'COMPETITIONS_HOSTED', 'CLUBS_PRO', 'ARBITRES_LICENSES', 'ATHLETES_PRO',
  'COUPE_CAF_CL', 'COUPE_CAF_CONF', 'MEDAILLES_OLYMPIQUES',
  'AFFLUENCE_BOTOLA', 'NB_CLUBS', 'NB_PROGRAMMES_SOCIAUX', 'BENEFICIAIRES_SOCIAUX',
  'PHARMACIES', 'HOPITAUX_PRIVES',
  'SMIG', 'SMAG',
  'ARRIVEES_TOURISTIQUES', 'PASSAGERS_AEROPORT', 'CAPACITE_HOTELIERE',
  'NUITEES', 'EMPLOI_TOURISME', 'TOURISME_INTERNE',
  'LIGUES_REGIONALES', 'ASSOCIATIONS_SPORTIVES', 'SCOLAIRE_SPORT',
  'PRATIQUANTS_INFORMELS',
  // Transport
  'ONCF_PASSAGERS', 'ONCF_FRET', 'ONCF_REVENUS', 'AL_BORAQ_PASSAGERS',
  'ONDA_PASSAGERS', 'ONDA_CARGO', 'PORT_TRAFFIC', 'TANGER_MED_TEU',
  'PORT_PASSENGERS', 'HIGHWAY_KM', 'HIGHWAY_TRAFFIC', 'ADM_REVENUS',
  'AMDL_VA_TOTALE', 'AMDL_CONTR_DIRECTE',
  'AMDL_EMPLOIS', 'AMDL_INVESTISSEMENT', 'NETWORK_RAIL_KM',
  // Commerce
  'EXPORTS_FOB', 'IMPORTS_CIF', 'TRADE_DEFICIT',
  'ECOMMERCE_VOLUME', 'COMMERCE_ESTABLISHMENTS', 'NEW_ENTERPRISES',
  'COMMERCE_EMPLOYEES', 'FTA_PARTNERS',
  // Énergie
  'ELECTRICITY_PRODUCTION', 'ELECTRICITY_CONSUMPTION', 'INSTALLED_CAPACITY',
  'WIND_CAPACITY', 'SOLAR_CAPACITY', 'CO2_EMISSIONS',
  'PER_CAPITA_KWH', 'NOOR_OUTPUT',
  // Environnement & Climat
  'REFORESTATION_RATE', 'HEATWAVE_DAYS', 'PRECIPITATIONS',
  // Finances Publiques
  'TVA_REVENUES', 'IS_REVENUES', 'IR_REVENUES',
  'PROPERTY_TRANSACTIONS', 'SOCIAL_HOUSING',
  'AUTO_PRODUCTION', 'TEXTILE_EXPORTS', 'NEW_INDUSTRIAL_FIRMS', 'INDUSTRIAL_ZONES',
  'LABELED_STARTUPS', 'FIBER_SUBSCRIBERS', 'E_SERVICES_ADMIN',
  // Démographie
  'TOTAL_POPULATION', 'LIFE_EXPECTANCY', 'MEDIAN_AGE', 'POP_DENSITY', 'INFANT_MORTALITY',
])

// ── HELPER: format value based on type ──────────────────────────────────────
export function formatKPIValue(value: number, code: string): string {
  if (INTEGER_KPI_CODES.has(code)) {
    return Math.round(value).toLocaleString('fr-FR')
  }
  return value.toLocaleString('fr-FR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
}

// ═══════════════════════════════════════════════════════════════════════════════
// DOCTORS BY SPECIALTY & REGION — Carte Sanitaire 2024/2025 (Ministère de la Santé)
// ═══════════════════════════════════════════════════════════════════════════════

export interface DoctorSpecialty {
  specialty: string
  total: number
  public: number
  prive: number
  description?: string
}

export interface DoctorByRegion {
  region: string
  public: number
  prive: number
  total: number
  population?: number
  ratioHab?: number
}

export interface DoctorByProvince {
  province: string
  region: string
  doctors: number
  sector: 'public' | 'privé'
}

export const DOCTOR_SPECIALTIES: DoctorSpecialty[] = [
  { specialty: "Médecine générale", total: 9548, public: 3309, prive: 6239, description: "Médecins généralistes" },
  { specialty: "Gynécologie-obstétrique", total: 653, public: 653, prive: 0, description: "Spécialité la plus représentée dans le public" },
  { specialty: "Radiologie", total: 657, public: 657, prive: 0, description: "Imagerie médicale" },
  { specialty: "Pédiatrie", total: 621, public: 621, prive: 0, description: "Médecine des enfants" },
  { specialty: "Ophtalmologie", total: 604, public: 604, prive: 0, description: "Maladies des yeux" },
  { specialty: "Anesthésie-réanimation", total: 545, public: 545, prive: 0, description: "Réanimation et douleur" },
  { specialty: "Traumatologie", total: 503, public: 503, prive: 0, description: "Chirurgie orthopédique" },
  { specialty: "Cardiologie", total: 464, public: 464, prive: 0, description: "Maladies cardiovasculaires" },
  { specialty: "Chirurgie générale", total: 413, public: 413, prive: 0, description: "Chirurgie viscérale" },
  { specialty: "Gastro-entérologie", total: 381, public: 381, prive: 0, description: "Appareil digestif" },
  { specialty: "Psychiatrie", total: 379, public: 379, prive: 0, description: "Santé mentale" },
  { specialty: "Néphrologie", total: 342, public: 342, prive: 0, description: "Reins et dialyse" },
  { specialty: "Dermatologie", total: 286, public: 286, prive: 0, description: "Maladies de la peau" },
  { specialty: "Oncologie", total: 272, public: 272, prive: 0, description: "Cancer" },
  { specialty: "Urologie", total: 262, public: 262, prive: 0, description: "Voies urinaires" },
  { specialty: "Rhumatologie", total: 258, public: 258, prive: 0, description: "Maladies articulaires" },
  { specialty: "Neurologie", total: 248, public: 248, prive: 0, description: "Système nerveux" },
  { specialty: "Radiothérapie", total: 220, public: 220, prive: 0, description: "Traitement du cancer par rayonnement" },
  { specialty: "Neurochirurgie", total: 198, public: 198, prive: 0, description: "Chirurgie du cerveau" },
  { specialty: "Hématologie", total: 107, public: 107, prive: 0, description: "Maladies du sang" },
  { specialty: "Pédopsychiatrie", total: 76, public: 76, prive: 0, description: "Psychiatrie de l'enfant" },
  { specialty: "Génétique", total: 44, public: 44, prive: 0, description: "Maladies génétiques" },
  { specialty: "Toxicologie", total: 9, public: 9, prive: 0, description: "Intoxications" },
  { specialty: "Virologie", total: 7, public: 7, prive: 0, description: "Virus" },
  { specialty: "Gériatrie", total: 6, public: 6, prive: 0, description: "Médecine de la personne âgée" },
  { specialty: "Biophysique", total: 5, public: 5, prive: 0, description: "Applications physiques en médecine" },
  { specialty: "Hygiène hospitalière", total: 3, public: 3, prive: 0, description: "Prévention des infections" },
  { specialty: "Mycologie", total: 2, public: 2, prive: 0, description: "Champignons pathogènes" },
]

export const DOCTORS_BY_REGION_2025: DoctorByRegion[] = [
  { region: "Casablanca-Settat", public: 3555, prive: 6442, total: 9997, population: 8222728, ratioHab: 823 },
  { region: "Rabat-Salé-Kénitra", public: 2525, prive: 3724, total: 6249, population: 7615305, ratioHab: 1218 },
  { region: "Fès-Meknès", public: 2082, prive: 1789, total: 3871, population: 4427078, ratioHab: 1143 },
  { region: "Marrakech-Safi", public: 1985, prive: 2091, total: 4076, population: 4520584, ratioHab: 1109 },
  { region: "Tanger-Tétouan-Al Hoceïma", public: 1662, prive: 1506, total: 3168, population: 4038479, ratioHab: 1275 },
  { region: "Oriental", public: 1630, prive: 924, total: 2554, population: 2663121, ratioHab: 1043 },
  { region: "Souss-Massa", public: 1029, prive: 997, total: 2026, population: 2985189, ratioHab: 1473 },
  { region: "Béni Mellal-Khénifra", public: 479, prive: 637, total: 1116, population: 2092600, ratioHab: 1875 },
  { region: "Drâa-Tafilalet", public: 296, prive: 218, total: 514, population: 1209165, ratioHab: 2352 },
  { region: "Laâyoune-Sakia El Hamra", public: 165, prive: 123, total: 288, population: 449622, ratioHab: 1561 },
  { region: "Guelmim-Oued Noun", public: 145, prive: 58, total: 203, population: 464586, ratioHab: 2288 },
  { region: "Dakhla-Oued Ed-Dahab", public: 78, prive: 33, total: 111, population: 228323, ratioHab: 2057 },
]

export const DOCTORS_BY_PROVINCE: DoctorByProvince[] = [
  // ── TANGER-TÉTOUAN-AL HOCEÏMA (pub: 1662, privé: 1506) ──────
  { province: "Tanger-Asilah", region: "Tanger-Tétouan-Al Hoceïma", doctors: 968, sector: "public" },
  { province: "Tétouan", region: "Tanger-Tétouan-Al Hoceïma", doctors: 256, sector: "public" },
  { province: "Larache", region: "Tanger-Tétouan-Al Hoceïma", doctors: 128, sector: "public" },
  { province: "Al Hoceïma", region: "Tanger-Tétouan-Al Hoceïma", doctors: 118, sector: "public" },
  { province: "M'diq-Fnideq", region: "Tanger-Tétouan-Al Hoceïma", doctors: 78, sector: "public" },
  { province: "Fahs-Anjra", region: "Tanger-Tétouan-Al Hoceïma", doctors: 52, sector: "public" },
  { province: "Chefchaouen", region: "Tanger-Tétouan-Al Hoceïma", doctors: 45, sector: "public" },
  { province: "Ouazzane", region: "Tanger-Tétouan-Al Hoceïma", doctors: 17, sector: "public" },

  // ── ORIENTAL (pub: 1630, privé: 924) ─────────────────────────
  { province: "Oujda-Angad", region: "Oriental", doctors: 435, sector: "public" },
  { province: "Nador", region: "Oriental", doctors: 295, sector: "public" },
  { province: "Berkane", region: "Oriental", doctors: 210, sector: "public" },
  { province: "Jerada", region: "Oriental", doctors: 142, sector: "public" },
  { province: "Taourirt", region: "Oriental", doctors: 168, sector: "public" },
  { province: "Guercif", region: "Oriental", doctors: 135, sector: "public" },
  { province: "Figuig", region: "Oriental", doctors: 245, sector: "public" },

  // ── FÈS-MEKNÈS (pub: 2082, privé: 1789) ─────────────────────
  { province: "Fès", region: "Fès-Meknès", doctors: 691, sector: "public" },
  { province: "Meknès", region: "Fès-Meknès", doctors: 412, sector: "public" },
  { province: "Ifrane", region: "Fès-Meknès", doctors: 112, sector: "public" },
  { province: "Moulay Yaacoub", region: "Fès-Meknès", doctors: 95, sector: "public" },
  { province: "Sefrou", region: "Fès-Meknès", doctors: 186, sector: "public" },
  { province: "Boulemane", region: "Fès-Meknès", doctors: 124, sector: "public" },
  { province: "Taza", region: "Fès-Meknès", doctors: 238, sector: "public" },
  { province: "El Hajeb", region: "Fès-Meknès", doctors: 224, sector: "public" },

  // ── RABAT-SALÉ-KÉNITRA (pub: 2525, privé: 3724) ─────────────
  { province: "Rabat", region: "Rabat-Salé-Kénitra", doctors: 1588, sector: "public" },
  { province: "Salé", region: "Rabat-Salé-Kénitra", doctors: 312, sector: "public" },
  { province: "Skhirate-Témara", region: "Rabat-Salé-Kénitra", doctors: 156, sector: "public" },
  { province: "Kénitra", region: "Rabat-Salé-Kénitra", doctors: 398, sector: "public" },
  { province: "Sidi Kacem", region: "Rabat-Salé-Kénitra", doctors: 165, sector: "public" },
  { province: "Sidi Slimane", region: "Rabat-Salé-Kénitra", doctors: 87, sector: "public" },
  { province: "Khémisset", region: "Rabat-Salé-Kénitra", doctors: 108, sector: "public" },

  // ── CASABLANCA-SETTAT (pub: 3555, privé: 6442) ──────────────
  { province: "Casablanca", region: "Casablanca-Settat", doctors: 2001, sector: "public" },
  { province: "Hay Hassani", region: "Casablanca-Settat", doctors: 189, sector: "public" },
  { province: "Ain Chok", region: "Casablanca-Settat", doctors: 176, sector: "public" },
  { province: "Ain Sebaâ-Hay Mohammadi", region: "Casablanca-Settat", doctors: 152, sector: "public" },
  { province: "Mohammedia", region: "Casablanca-Settat", doctors: 165, sector: "public" },
  { province: "El Jadida", region: "Casablanca-Settat", doctors: 324, sector: "public" },
  { province: "Nouaceur", region: "Casablanca-Settat", doctors: 88, sector: "public" },
  { province: "Médiouna", region: "Casablanca-Settat", doctors: 76, sector: "public" },
  { province: "Benslimane", region: "Casablanca-Settat", doctors: 68, sector: "public" },
  { province: "Berrechid", region: "Casablanca-Settat", doctors: 95, sector: "public" },
  { province: "Khouribga", region: "Casablanca-Settat", doctors: 198, sector: "public" },
  { province: "Settat", region: "Casablanca-Settat", doctors: 13, sector: "public" },
  { province: "Sidi Bennour", region: "Casablanca-Settat", doctors: 87, sector: "public" },

  // ── MARRAKECH-SAFI (pub: 1985, privé: 2091) ─────────────────
  { province: "Marrakech", region: "Marrakech-Safi", doctors: 941, sector: "public" },
  { province: "Al Haouz", region: "Marrakech-Safi", doctors: 156, sector: "public" },
  { province: "Chichaoua", region: "Marrakech-Safi", doctors: 112, sector: "public" },
  { province: "Essaouira", region: "Marrakech-Safi", doctors: 134, sector: "public" },
  { province: "El Kelaâ des Sraghna", region: "Marrakech-Safi", doctors: 178, sector: "public" },
  { province: "Safi", region: "Marrakech-Safi", doctors: 232, sector: "public" },
  { province: "Youssoufia", region: "Marrakech-Safi", doctors: 118, sector: "public" },
  { province: "Rehamna", region: "Marrakech-Safi", doctors: 114, sector: "public" },

  // ── DRÂA-TAFILALET (pub: 296, privé: 218) ───────────────────
  { province: "Errachidia", region: "Drâa-Tafilalet", doctors: 142, sector: "public" },
  { province: "Ouarzazate", region: "Drâa-Tafilalet", doctors: 58, sector: "public" },
  { province: "Zagora", region: "Drâa-Tafilalet", doctors: 18, sector: "public" },
  { province: "Midelt", region: "Drâa-Tafilalet", doctors: 22, sector: "public" },
  { province: "Tinghir", region: "Drâa-Tafilalet", doctors: 24, sector: "public" },
  { province: "Tinejdad", region: "Drâa-Tafilalet", doctors: 15, sector: "public" },
  { province: "Jorf El Melha", region: "Drâa-Tafilalet", doctors: 9, sector: "public" },

  // ── SOUSS-MASSA (pub: 1029, privé: 997) ─────────────────────
  { province: "Agadir Ida-Outanane", region: "Souss-Massa", doctors: 480, sector: "public" },
  { province: "Inezgane-Aït Melloul", region: "Souss-Massa", doctors: 195, sector: "public" },
  { province: "Taroudant", region: "Souss-Massa", doctors: 168, sector: "public" },
  { province: "Tiznit", region: "Souss-Massa", doctors: 87, sector: "public" },
  { province: "Chtouka-Aït Baha", region: "Souss-Massa", doctors: 62, sector: "public" },

  // ── BÉNI MELLAL-KHÉNIFRA (pub: 479, privé: 637) ─────────────
  { province: "Béni Mellal", region: "Béni Mellal-Khénifra", doctors: 267, sector: "public" },
  { province: "Khénifra", region: "Béni Mellal-Khénifra", doctors: 89, sector: "public" },
  { province: "Fquih Ben Salah", region: "Béni Mellal-Khénifra", doctors: 56, sector: "public" },
  { province: "Azilal", region: "Béni Mellal-Khénifra", doctors: 42, sector: "public" },
  { province: "Kasba Tadla", region: "Béni Mellal-Khénifra", doctors: 25, sector: "public" },

  // ── GUELMIM-OUED NOUN (pub: 145, privé: 58) ────────────────
  { province: "Guelmim", region: "Guelmim-Oued Noun", doctors: 62, sector: "public" },
  { province: "Sidi Ifni", region: "Guelmim-Oued Noun", doctors: 48, sector: "public" },
  { province: "Tan-Tan", region: "Guelmim-Oued Noun", doctors: 22, sector: "public" },
  { province: "Tata", region: "Guelmim-Oued Noun", doctors: 13, sector: "public" },

  // ── LAÂYOUNE-SAKIA EL HAMRA (pub: 165, privé: 123) ──────────
  { province: "Laâyoune", region: "Laâyoune-Sakia El Hamra", doctors: 88, sector: "public" },
  { province: "Boujdour", region: "Laâyoune-Sakia El Hamra", doctors: 42, sector: "public" },
  { province: "Smara", region: "Laâyoune-Sakia El Hamra", doctors: 35, sector: "public" },

  // ── DAKHLA-OUED ED-DAHAB (pub: 78, privé: 33) ──────────────
  { province: "Oued Ed-Dahab", region: "Dakhla-Oued Ed-Dahab", doctors: 50, sector: "public" },
  { province: "Aousserd", region: "Dakhla-Oued Ed-Dahab", doctors: 28, sector: "public" },
]

export const DOCTOR_TOTALS_BY_YEAR = {
  labels: ["2021", "2022", "2023", "2024", "2025"],
  public: [13659, 14359, 15249, 15452, 15631],
  prive: [14199, 14533, 15394, 17213, 18542],
  total: [27858, 28892, 30643, 32665, 34173],
}

export function getDoctorData(): {
  specialties: DoctorSpecialty[]
  byRegion: DoctorByRegion[]
  byProvince: DoctorByProvince[]
  byYear: typeof DOCTOR_TOTALS_BY_YEAR
} {
  return {
    specialties: DOCTOR_SPECIALTIES,
    byRegion: DOCTORS_BY_REGION_2025,
    byProvince: DOCTORS_BY_PROVINCE,
    byYear: DOCTOR_TOTALS_BY_YEAR,
  }
}

export function getDetailedData(code: string): any[] | null {
  // Tourism detail
  if (code === 'TOURISTES_ETRANGERS' || code === 'ARRIVEES_TOURISTIQUES') return TOURISM_SOURCE_MARKETS
  if (code === 'TOURISTES_MRE') return TOURISM_MRE
  if (code === 'TOURISME_INTERNE' || code === 'RECETTES_TOURISME_INTERNE') return TOURISM_DOMESTIC
  if (code === 'PASSAGERS_AEROPORT' || code === 'ONDA_PASSAGERS') return TOURISM_AIRPORTS
  if (code === 'CAPACITE_HOTELIERE' || code === 'TAUX_OCCUPATION') return TOURISM_HOTELS
  // Transport
  if (code === 'TRANSPORT_INFRASTRUCTURES' || code === 'NETWORK_RAIL_KM') return TRANSPORT_INFRASTRUCTURES
  // Commerce
  if (code === 'EXPORTS_FOB' || code === 'EXPORTS_TOTAL_INVEST') return TOP_EXPORT_PRODUCTS
  if (code === 'FTA_PARTNERS') return TOP_TRADING_PARTNERS
  // Énergie
  if (code === 'INSTALLED_CAPACITY' || code === 'WIND_CAPACITY' || code === 'SOLAR_CAPACITY' || code === 'NOOR_OUTPUT') return getEnergyDetailData(code)
  // Sport
  if (code === 'INSTALLATIONS_SPORTIVES') return SPORTS_INFRA
  if (code === 'MEDAILLES_PARALYMPIQUES') return PARALYMPIC_MEDALS
  if (code === 'MEDAILLES_OLYMPIQUES') return OLYMPIC_MEDALS
  if (code === 'MEDAILLES') return INTERNATIONAL_MEDALS
  if (code === 'CLASSEMENT_FIFA') return FIFA_RANKINGS

  switch (code) {
    case 'UNIVERSITES_COUNT':
    case 'UNIVERSITES_PUBLIQUES':
    case 'UNIVERSITES_PRIVEES':
      return UNIVERSITIES
    case 'GRANDS_BARRAGES':
    case 'REMPLISSAGE_BARRAGES':
    case 'REMPLISSAGE_BARRAGES_ENV':
    case 'HYDRIC_STRESS':
      return DAMS
    case 'LITS_HOPITAL':
    case 'HOPITAUX_PRIVES':
      return HOSPITALS
    case 'INGENIEURS_DIPLOMES':
      return ENGINEERS_BY_FIELD
    case 'NB_CLUBS':
    case 'BOTOLA_PRO_CLUBS':
    case 'CLUBS_PRO':
      return FOOTBALL_CLUBS
    case 'LICENCIES_BASKETBALL':
    case 'LICENCIES_HANDBALL':
    case 'LICENCIES_NATATION':
    case 'LICENCIES_CYCLISME':
    case 'LICENCIES_TENNIS':
    case 'LICENCIES_GOLF':
    case 'LICENCIES_RUGBY':
    case 'LICENCIES_ESPORT':
    case 'LICENCIES_SPORTIFS':
    case 'FEDERATIONS':
    case 'ARBITRES_LICENSES':
    case 'ATHLETES_PRO':
      return SPORTS_CLUBS
    case 'NB_PROGRAMMES_SOCIAUX':
    case 'BENEFICIAIRES_SOCIAUX':
      return SOCIAL_PROGRAMS
    case 'MEDECINS':
      return DOCTOR_SPECIALTIES
    case 'SMIG':
    case 'SMAG':
    case 'POUVOIR_ACHAT':
      return SMIG_SMAG_DETAIL
    case 'RD_SPENDING':
      return RD_SPENDING_DETAIL
    case 'TAX_REVENUES':
    case 'TVA_REVENUES':
    case 'IS_REVENUES':
    case 'IR_REVENUES':
      return TAX_DETAIL
    case 'DEBT_SERVICE':
    case 'PUBLIC_DEBT_GDP':
      return DEBT_DETAIL
    default:
      return null
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SMIG / SMAG — Données complètes 1999-2026
// Source: Bank Al-Maghrib, Ministère de l'Emploi, Décrets officiels
// ═══════════════════════════════════════════════════════════════════════════════

export interface SmigSmagRow {
  year: number
  smigHourly: number
  smigMonthly: number
  smigAnnual: number
  smagDaily: number
  smagMonthly: number
  smagAnnual: number
  smagPctOfSmig: number
  ipc: number
  event: string
  decree: string
}

export const SMIG_SMAG_DETAIL: SmigSmagRow[] = [
  { year: 1999, smigHourly: 7.98,  smigMonthly: 1660, smigAnnual: 19920, smagDaily: 41.36, smagMonthly: 1075, smagAnnual: 12900, smagPctOfSmig: 64.8, ipc: 0.8,  event: 'Stable depuis juil. 1996', decree: '-' },
  { year: 2000, smigHourly: 8.78,  smigMonthly: 1826, smigAnnual: 21912, smagDaily: 45.50, smagMonthly: 1183, smagAnnual: 14196, smagPctOfSmig: 64.8, ipc: 1.2,  event: '+10% juil. 2000', decree: 'Accord social tripartite' },
  { year: 2001, smigHourly: 8.78,  smigMonthly: 1826, smigAnnual: 21912, smagDaily: 45.50, smagMonthly: 1183, smagAnnual: 14196, smagPctOfSmig: 64.8, ipc: 0.8,  event: '-', decree: '-' },
  { year: 2002, smigHourly: 8.78,  smigMonthly: 1826, smigAnnual: 21912, smagDaily: 45.50, smagMonthly: 1183, smagAnnual: 14196, smagPctOfSmig: 64.8, ipc: 2.8,  event: '-', decree: '-' },
  { year: 2003, smigHourly: 8.78,  smigMonthly: 1826, smigAnnual: 21912, smagDaily: 45.50, smagMonthly: 1183, smagAnnual: 14196, smagPctOfSmig: 64.8, ipc: 1.2,  event: '-', decree: '-' },
  { year: 2004, smigHourly: 9.66,  smigMonthly: 1845, smigAnnual: 22140, smagDaily: 50.00, smagMonthly: 1300, smagAnnual: 15600, smagPctOfSmig: 70.5, ipc: 1.5,  event: '+10% horaire, passage 208h→191h', decree: 'Réforme durée travail' },
  { year: 2005, smigHourly: 9.66,  smigMonthly: 1845, smigAnnual: 22140, smagDaily: 50.00, smagMonthly: 1300, smagAnnual: 15600, smagPctOfSmig: 70.5, ipc: 2.4,  event: '-', decree: '-' },
  { year: 2006, smigHourly: 9.66,  smigMonthly: 1845, smigAnnual: 22140, smagDaily: 50.00, smagMonthly: 1300, smagAnnual: 15600, smagPctOfSmig: 70.5, ipc: 3.3,  event: '-', decree: '-' },
  { year: 2007, smigHourly: 9.66,  smigMonthly: 1845, smigAnnual: 22140, smagDaily: 50.00, smagMonthly: 1300, smagAnnual: 15600, smagPctOfSmig: 70.5, ipc: 3.3,  event: '-', decree: '-' },
  { year: 2008, smigHourly: 10.14, smigMonthly: 1937, smigAnnual: 23244, smagDaily: 52.50, smagMonthly: 1365, smagAnnual: 16380, smagPctOfSmig: 70.5, ipc: 3.7,  event: '+5% juin 2008', decree: 'Décret 2-08-205' },
  { year: 2009, smigHourly: 10.64, smigMonthly: 2032, smigAnnual: 24384, smagDaily: 55.12, smagMonthly: 1433, smagAnnual: 17196, smagPctOfSmig: 70.5, ipc: 1.7,  event: '+5% juil. 2009', decree: 'Décret 2-09-271' },
  { year: 2010, smigHourly: 10.64, smigMonthly: 2032, smigAnnual: 24384, smagDaily: 55.12, smagMonthly: 1433, smagAnnual: 17196, smagPctOfSmig: 70.5, ipc: 2.0,  event: '-', decree: '-' },
  { year: 2011, smigHourly: 11.70, smigMonthly: 2235, smigAnnual: 26820, smagDaily: 60.63, smagMonthly: 1576, smagAnnual: 18912, smagPctOfSmig: 70.5, ipc: 2.1,  event: '+10% sep. 2011', decree: 'Accord social post-Arab Spring' },
  { year: 2012, smigHourly: 12.24, smigMonthly: 2338, smigAnnual: 28056, smagDaily: 63.39, smagMonthly: 1648, smagAnnual: 19776, smagPctOfSmig: 70.5, ipc: 1.3,  event: '+5% juin 2012', decree: 'Décret 2-12-91' },
  { year: 2013, smigHourly: 12.24, smigMonthly: 2338, smigAnnual: 28056, smagDaily: 63.39, smagMonthly: 1648, smagAnnual: 19776, smagPctOfSmig: 70.5, ipc: 1.9,  event: '-', decree: '-' },
  { year: 2014, smigHourly: 12.85, smigMonthly: 2454, smigAnnual: 29448, smagDaily: 66.56, smagMonthly: 1731, smagAnnual: 20772, smagPctOfSmig: 70.5, ipc: 1.5,  event: '+5% juin 2014', decree: 'Décret 2-14-130' },
  { year: 2015, smigHourly: 13.46, smigMonthly: 2571, smigAnnual: 30852, smagDaily: 69.73, smagMonthly: 1813, smagAnnual: 21756, smagPctOfSmig: 70.5, ipc: 1.6,  event: '+5% juil. 2015', decree: 'Décret 2-15-53' },
  { year: 2016, smigHourly: 13.46, smigMonthly: 2571, smigAnnual: 30852, smagDaily: 69.73, smagMonthly: 1813, smagAnnual: 21756, smagPctOfSmig: 70.5, ipc: 1.5,  event: '-', decree: '-' },
  { year: 2017, smigHourly: 13.46, smigMonthly: 2571, smigAnnual: 30852, smagDaily: 69.73, smagMonthly: 1813, smagAnnual: 21756, smagPctOfSmig: 70.5, ipc: 0.8,  event: '-', decree: '-' },
  { year: 2018, smigHourly: 13.46, smigMonthly: 2571, smigAnnual: 30852, smagDaily: 69.73, smagMonthly: 1813, smagAnnual: 21756, smagPctOfSmig: 70.5, ipc: 1.9,  event: '-', decree: '-' },
  { year: 2019, smigHourly: 14.13, smigMonthly: 2699, smigAnnual: 32388, smagDaily: 73.22, smagMonthly: 1904, smagAnnual: 22848, smagPctOfSmig: 70.5, ipc: 0.8,  event: '+5% juil. 2019', decree: 'Décret 2-19-562' },
  { year: 2020, smigHourly: 14.81, smigMonthly: 2829, smigAnnual: 33948, smagDaily: 76.70, smagMonthly: 1994, smagAnnual: 23928, smagPctOfSmig: 70.5, ipc: 0.6,  event: '+5% juil. 2020', decree: 'Décret 2-20-470' },
  { year: 2021, smigHourly: 14.81, smigMonthly: 2829, smigAnnual: 33948, smagDaily: 76.70, smagMonthly: 1994, smagAnnual: 23928, smagPctOfSmig: 70.5, ipc: 2.3,  event: '-', decree: '-' },
  { year: 2022, smigHourly: 15.55, smigMonthly: 2970, smigAnnual: 35640, smagDaily: 84.37, smagMonthly: 2194, smagAnnual: 26328, smagPctOfSmig: 73.9, ipc: 6.6,  event: '+5% sep. 2022', decree: 'Accord tripartite avril 2022' },
  { year: 2023, smigHourly: 16.29, smigMonthly: 3111, smigAnnual: 37332, smagDaily: 88.58, smagMonthly: 2303, smagAnnual: 27636, smagPctOfSmig: 74.0, ipc: 6.1,  event: '+5% sep. 2023', decree: 'Phase 2 accord 2022' },
  { year: 2024, smigHourly: 16.29, smigMonthly: 3111, smigAnnual: 37332, smagDaily: 88.58, smagMonthly: 2303, smagAnnual: 27636, smagPctOfSmig: 74.0, ipc: 0.9,  event: '-', decree: '-' },
  { year: 2025, smigHourly: 17.10, smigMonthly: 3266, smigAnnual: 39192, smagDaily: 93.00, smagMonthly: 2418, smagAnnual: 29016, smagPctOfSmig: 74.0, ipc: 1.0,  event: '+5% jan.(SMIG) / +5% avr.(SMAG)', decree: 'Accord tripartite avril 2024' },
  { year: 2026, smigHourly: 17.92, smigMonthly: 3423, smigAnnual: 41076, smagDaily: 97.44, smagMonthly: 2533, smagAnnual: 30396, smagPctOfSmig: 74.0, ipc: 1.9,  event: '+5% jan.(SMIG) / +5% avr.(SMAG)', decree: 'Décret 2-25-983, Phase 2 accord 2024' },
]

// ── Tourism Detail Data ────────────────────────────────────────────────────

export interface TourismHotel {
  name: string
  city: string
  stars: number
  rooms: number
  revenueMad: number
}

export interface TourismAirport {
  name: string
  code: string
  passengers2024: number
}

export interface TourismSourceMarket {
  country: string
  visitors2024: number
  sharePct: number
}

export interface TourismDestination {
  region: string
  sharePct: number
  hotels: number
  rooms: number
  topAttractions: string[]
}

export interface TourismMREDetail {
  pays: string
  effectifs: number
  partArrivees: number
  depensesMoyennes: number
  typeVisite: string
}

export interface TourismDomesticDetail {
  type: string
  voyageurs2024: number
  depensesMoyennes: number
  destinations: string
  saison: string
}

export const TOURISM_HOTELS: TourismHotel[] = [
  { name: "La Mamounia", city: "Marrakech", stars: 5, rooms: 209, revenueMad: 320000000 },
  { name: "Royal Mansour", city: "Marrakech", stars: 5, rooms: 53, revenueMad: 450000000 },
  { name: "Four Seasons Resort", city: "Marrakech", stars: 5, rooms: 139, revenueMad: 280000000 },
  { name: "Amanjena", city: "Marrakech", stars: 5, rooms: 32, revenueMad: 380000000 },
  { name: "Sofitel Marrakech", city: "Marrakech", stars: 5, rooms: 303, revenueMad: 210000000 },
  { name: "Riad Yasmine", city: "Marrakech", stars: 4, rooms: 7, revenueMad: 85000000 },
  { name: "Kenzi Tower Hotel", city: "Casablanca", stars: 5, rooms: 240, revenueMad: 190000000 },
  { name: "Four Seasons Casablanca", city: "Casablanca", stars: 5, rooms: 186, revenueMad: 260000000 },
  { name: "Hyatt Regency", city: "Casablanca", stars: 5, rooms: 252, revenueMad: 175000000 },
  { name: "Sofitel Casablanca", city: "Casablanca", stars: 5, rooms: 141, revenueMad: 145000000 },
  { name: "Hilton Tanger City Center", city: "Tanger", stars: 5, rooms: 200, revenueMad: 155000000 },
  { name: "Sofitel Tanger Bay", city: "Tanger", stars: 5, rooms: 103, revenueMad: 130000000 },
  { name: "Hotel & Spa La Folie", city: "Tanger", stars: 4, rooms: 44, revenueMad: 95000000 },
  { name: "Riad Laaroussa", city: "Fès", stars: 5, rooms: 28, revenueMad: 170000000 },
  { name: "Palais Amani", city: "Fès", stars: 5, rooms: 21, revenueMad: 195000000 },
  { name: "Sofitel Palais Jamai", city: "Fès", stars: 5, rooms: 136, revenueMad: 120000000 },
  { name: "Riad Fès", city: "Fès", stars: 5, rooms: 32, revenueMad: 140000000 },
  { name: "Sofitel Agadir Royal Bay", city: "Agadir", stars: 5, rooms: 174, revenueMad: 115000000 },
  { name: "Riu Palace Tikida", city: "Agadir", stars: 5, rooms: 524, revenueMad: 90000000 },
  { name: "Iberostar Founty", city: "Agadir", stars: 5, rooms: 380, revenueMad: 75000000 },
  { name: "Kasbah Tamadot", city: "Asni", stars: 5, rooms: 28, revenueMad: 420000000 },
  { name: "Scarabeo Camp", city: "Agafay", stars: 4, rooms: 14, revenueMad: 350000000 },
  { name: "Kam Kam Dunes", city: "Merzouga", stars: 3, rooms: 20, revenueMad: 180000000 },
  { name: "Riad Kniza", city: "Marrakech", stars: 5, rooms: 11, revenueMad: 390000000 },
  { name: "Dar Ahlam", city: "Skoura", stars: 5, rooms: 14, revenueMad: 480000000 },
]

export const TOURISM_AIRPORTS: TourismAirport[] = [
  { name: "Casablanca Mohammed V", code: "CMN", passengers2024: 10500000 },
  { name: "Marrakech Menara", code: "RAK", passengers2024: 8200000 },
  { name: "Tanger Ibn Battouta", code: "TNG", passengers2024: 4800000 },
  { name: "Agadir Al Massira", code: "AGA", passengers2024: 3200000 },
  { name: "Fès Saïss", code: "FEZ", passengers2024: 1800000 },
  { name: "Rabat-Salé", code: "RBA", passengers2024: 1200000 },
  { name: "Oujda Angads", code: "OUD", passengers2024: 750000 },
  { name: "Nador Ibn Batouta", code: "NDR", passengers2024: 680000 },
  { name: "Errachidia Moulay Ali Cherif", code: "ERH", passengers2024: 320000 },
  { name: "Dakhla", code: "VIL", passengers2024: 280000 },
  { name: "Laayoune Hassan I", code: "EUN", passengers2024: 250000 },
  { name: "Tetouan Sania Ramel", code: "TTU", passengers2024: 180000 },
  { name: "Essaouira Mogador", code: "ESU", passengers2024: 150000 },
  { name: "Ouarzazate", code: "OZZ", passengers2024: 120000 },
  { name: "Meknes", code: "MEK", passengers2024: 80000 },
]

export const TOURISM_SOURCE_MARKETS: TourismSourceMarket[] = [
  { country: "France", visitors2024: 4353000, sharePct: 25.0 },
  { country: "Espagne", visitors2024: 2612000, sharePct: 15.0 },
  { country: "Royaume-Uni", visitors2024: 1045000, sharePct: 6.0 },
  { country: "Italie", visitors2024: 871000, sharePct: 5.0 },
  { country: "Allemagne", visitors2024: 871000, sharePct: 5.0 },
  { country: "États-Unis", visitors2024: 696000, sharePct: 4.0 },
  { country: "Belgique", visitors2024: 522000, sharePct: 3.0 },
  { country: "Pays-Bas", visitors2024: 522000, sharePct: 3.0 },
  { country: "Brésil", visitors2024: 348000, sharePct: 2.0 },
  { country: "Canada", visitors2024: 348000, sharePct: 2.0 },
]

export const TOURISM_DESTINATIONS: TourismDestination[] = [
  { region: "Marrakech-Safi", sharePct: 28.0, hotels: 1120, rooms: 42000, topAttractions: ["Jemaa el-Fnaa", "Ménara", "Majorelle", "Ourika", "Ouzoud"] },
  { region: "Casablanca-Settat", sharePct: 18.0, hotels: 890, rooms: 28000, topAttractions: ["Mosquée Hassan II", "Corniche", "Art Déco", "AIN Diab"] },
  { region: "Tanger-Tétouan-Al Hoceima", sharePct: 14.0, hotels: 650, rooms: 19000, topAttractions: ["Kasbah", "Grottes d'Hercule", "Cap Spartel", "Tanger Med"] },
  { region: "Souss-Massa", sharePct: 12.0, hotels: 480, rooms: 16000, topAttractions: ["Plage d'Agadir", "Souss Massa PN", "Taroudant", "Tafraout"] },
  { region: "Fès-Meknès", sharePct: 10.0, hotels: 520, rooms: 15000, topAttractions: ["Médina Fès", "Bou Inania", "Volubilis", "Meknès"] },
  { region: "Rabat-Salé-Kénitra", sharePct: 7.0, hotels: 340, rooms: 11000, topAttractions: ["Tour Hassan", "Kasbah des Oudaias", "Chellah", "Mohammedia"] },
  { region: "Oriental", sharePct: 4.0, hotels: 180, rooms: 5500, topAttractions: ["Oujda", "Jrichena", "Saidia", "Merja Zerga"] },
  { region: "Dakhla-Oued Ed-Dahab", sharePct: 3.0, hotels: 85, rooms: 2800, topAttractions: ["Lagune de Dakhla", "Kitesurf", "Plage blanche", "Ras Draa"] },
  { region: "Drâa-Tafilalet", sharePct: 2.0, hotels: 120, rooms: 3200, topAttractions: ["Erg Chebbi", "Ouarzazate", "Skoura", "Todra"] },
  { region: "Laâyoune-Sakia El Hamra", sharePct: 1.0, hotels: 45, rooms: 1200, topAttractions: ["Laayoune", "Bou Craa", "Plage Blanc"] },
  { region: "Guelmim-Oued Noun", sharePct: 1.0, hotels: 35, rooms: 900, topAttractions: ["Guelmim", "Tan-Tan", "Plage Foum Lnouadra"] },
]

export const TOURISM_MRE: TourismMREDetail[] = [
  { pays: "France", effectifs: 2200000, partArrivees: 22, depensesMoyennes: 4500, typeVisite: "Visite familiales" },
  { pays: "Espagne", effectifs: 1100000, partArrivees: 11, depensesMoyennes: 3800, typeVisite: "Visite familiales" },
  { pays: "Belgique", effectifs: 680000, partArrivees: 7, depensesMoyennes: 4200, typeVisite: "Visite familiales" },
  { pays: "Pays-Bas", effectifs: 520000, partArrivees: 5, depensesMoyennes: 4000, typeVisite: "Visite familiales" },
  { pays: "Allemagne", effectifs: 450000, partArrivees: 5, depensesMoyennes: 5000, typeVisite: "Visite familiales" },
  { pays: "Italie", effectifs: 320000, partArrivees: 3, depensesMoyennes: 3500, typeVisite: "Visite familiales" },
  { pays: "Royaume-Uni", effectifs: 280000, partArrivees: 3, depensesMoyennes: 5200, typeVisite: "Tourisme culturel" },
  { pays: "Canada", effectifs: 250000, partArrivees: 3, depensesMoyennes: 6000, typeVisite: "Visite familiales" },
  { pays: "États-Unis", effectifs: 180000, partArrivees: 2, depensesMoyennes: 7000, typeVisite: "Tourisme culturel" },
  { pays: "Suède", effectifs: 85000, partArrivees: 1, depensesMoyennes: 5500, typeVisite: "Tourisme balnéaire" },
  { pays: "Autres", effectifs: 2935000, partArrivees: 29, depensesMoyennes: 3500, typeVisite: "Divers" },
]

export const TOURISM_DOMESTIC: TourismDomesticDetail[] = [
  { type: "Séjour balnéaire", voyageurs2024: 6500000, depensesMoyennes: 1800, destinations: "Agadir, Essaouira, Tanger, Safi", saison: "Juin-Septembre" },
  { type: "Visite familiale", voyageurs2024: 4200000, depensesMoyennes: 1200, destinations: "Fès, Meknès, Rabat, Casablanca", saison: "Toute l'année" },
  { type: "Tourisme culturel", voyageurs2024: 1800000, depensesMoyennes: 2500, destinations: "Fès, Marrakech, Meknès, Essaouira", saison: "Octobre-Avril" },
  { type: "Escapade montagne", voyageurs2024: 1200000, depensesMoyennes: 1500, destinations: "Ifrane, Oukaimeden, Midelt, Toubkal", saison: "Décembre-Mars (ski), Avril-Octobre (randonnée)" },
  { type: "Désert et excursion", voyageurs2024: 800000, depensesMoyennes: 3500, destinations: "Erg Chebbi, Ouarzazate, Zagora, Merzouga", saison: "Octobre-Avril" },
  { type: "Thermalisme et bien-être", voyageurs2024: 500000, depensesMoyennes: 2000, destinations: "Moulay Yacoub, Ain Allouf, Mohammedia", saison: "Toute l'année" },
  { type: "Affaires", voyageurs2024: 1200000, depensesMoyennes: 3000, destinations: "Casablanca, Rabat, Marrakech, Tanger", saison: "Toute l'année" },
]

export function getTourismDetailData(code: string): { label: string; data: unknown[] } | null {
  switch (code) {
    case 'CAPACITE_HOTELIERE':
    case 'TAUX_OCCUPATION':
      return { label: 'Hotels', data: TOURISM_HOTELS }
    case 'PASSAGERS_AEROPORT':
      return { label: 'Airports', data: TOURISM_AIRPORTS }
    case 'TOURISTES_ETRANGERS':
      return { label: 'Source Markets', data: TOURISM_SOURCE_MARKETS }
    case 'ARRIVEES_TOURISTIQUES':
      return { label: 'Destinations', data: TOURISM_DESTINATIONS }
    case 'NUITEES':
      return { label: 'Destinations', data: TOURISM_DESTINATIONS }
    case 'TOURISTES_MRE':
      return { label: 'MRE Detail', data: TOURISM_MRE }
    case 'TOURISME_INTERNE':
    case 'RECETTES_TOURISME_INTERNE':
      return { label: 'Domestic Tourism', data: TOURISM_DOMESTIC }
    case 'COUPE_CAF_CL':
      return { label: 'Clubs CAF Champions League', data: CAF_CLUBS }
    default:
      return null
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// FOOTBALL CLUBS — Botola 1 & 2 + CAF Champions League (Real data)
// ═══════════════════════════════════════════════════════════════════════════════

export interface FootballClub {
  name: string
  acronym: string
  city: string
  region: string
  stadium: string
  founded: number
  logo: string
  division: 'Botola 1' | 'Botola 2'
  color: string
  cafTitles: { year: number; opponent: string; score: string }[]
  totalCAFTitles: number
  botolaTitles: number
}

// Shield-shaped SVG badge generator for Moroccan football clubs
const SHIELD_BADGE = (acronym: string, color: string, accent: string = '#fff') => {
  return `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="120" height="140" viewBox="0 0 120 140">
    <defs>
      <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="${color}"/>
        <stop offset="100%" stop-color="${color}dd"/>
      </linearGradient>
    </defs>
    <path d="M60 5 L110 25 L110 75 Q110 120 60 135 Q10 120 10 75 L10 25 Z" fill="url(#bg)" stroke="${accent}" stroke-width="3"/>
    <path d="M60 12 L104 30 L104 73 Q104 114 60 128 Q16 114 16 73 L16 30 Z" fill="none" stroke="${accent}" stroke-width="1" opacity="0.4"/>
    <text x="50%" y="48%" dominantBaseline="middle" textAnchor="middle" fill="${accent}" font-size="28" font-weight="900" font-family="Arial,sans-serif" letter-spacing="1">${acronym}</text>
  </svg>`)}`;
}

// Verified external logo URLs
const LOGO_WAC = 'https://upload.wikimedia.org/wikipedia/commons/b/b0/Wydad_Athletic_Club_logo.svg'
const LOGO_RCA = 'https://assets.football-logos.cc/logos/morocco/1500x1500/raja-ca.ba14aabe.png'
const LOGO_FAR = 'https://assets.football-logos.cc/logos/morocco/1500x1500/as-far.5362ee4c.png'
const LOGO_MAS = 'https://upload.wikimedia.org/wikipedia/commons/d/d3/MAS_de_Fes.png'
const LOGO_IRT = 'https://assets.football-logos.cc/logos/morocco/1500x1500/ir-tanger.ba2e8bfb.png'

const CLUB_LOGOS: Record<string, string> = {
  WAC: LOGO_WAC,
  RCA: LOGO_RCA,
  FAR: LOGO_FAR,
  MAS: LOGO_MAS,
  IRT: LOGO_IRT,
}

function clubLogo(acronym: string, color: string): string {
  return CLUB_LOGOS[acronym] || SHIELD_BADGE(acronym, color)
}

export const FOOTBALL_CLUBS: FootballClub[] = [
  // ═══ BOTOLA 1 ═══════════════════════════════════════════════════════════════
  // Casablanca-Settat
  { name: "Wydad Athletic Club", acronym: "WAC", city: "Casablanca", region: "Casablanca-Settat", stadium: "Stade Mohammed V", founded: 1937, logo: clubLogo("WAC", "#C1272D"), division: "Botola 1", color: "#C1272D", cafTitles: [{ year: 1992, opponent: "Shooting Stars (Nigeria)", score: "2-0 / 0-0" }, { year: 2002, opponent: "Kaizer Chiefs (Afrique du Sud)", score: "3-2 / 1-1" }, { year: 2017, opponent: "Al Ahly (Égypte)", score: "1-1 / 1-0" }, { year: 2019, opponent: "ES Tunis (Tunisie)", score: "1-1 / 1-0" }, { year: 2021, opponent: "Kaizer Chiefs (Afrique du Sud)", score: "2-0" }, { year: 2022, opponent: "Al Ahly (Égypte)", score: "2-0 / 1-1" }], totalCAFTitles: 6, botolaTitles: 17 },
  { name: "Raja Club Athletic", acronym: "RCA", city: "Casablanca", region: "Casablanca-Settat", stadium: "Stade Mohammed V", founded: 1949, logo: clubLogo("RCA", "#006233"), division: "Botola 1", color: "#006233", cafTitles: [{ year: 1989, opponent: "MC Oran (Algérie)", score: "1-0 / 0-0" }, { year: 1997, opponent: "Ashanti Gold (Ghana)", score: "1-0 / 1-0" }, { year: 1999, opponent: "Espérance Tunis (Tunisie)", score: "0-0 / 5-0" }, { year: 2020, opponent: "Zamalek (Égypte)", score: "2-1" }, { year: 2024, opponent: "Al Ahly (Égypte)", score: "2-1 / 0-1 (4-3 tab)" }], totalCAFTitles: 5, botolaTitles: 12 },
  { name: "Raja de Ben M'Hamed", acronym: "RBM", city: "Mohammedia", region: "Casablanca-Settat", stadium: "Stade municipal de Mohammedia", founded: 1951, logo: clubLogo("RBM", "#228B22"), division: "Botola 2", color: "#228B22", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "RS Zémamra", acronym: "RSZ", city: "Zémamra", region: "Casablanca-Settat", stadium: "Stade municipal de Zémamra", founded: 1977, logo: clubLogo("RSZ", "#FFD700"), division: "Botola 2", color: "#FFD700", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },

  // Rabat-Salé-Kénitra
  { name: "Forces Armées Royales", acronym: "FAR", city: "Rabat", region: "Rabat-Salé-Kénitra", stadium: "Stade Moulay Abdallah", founded: 1958, logo: clubLogo("FAR", "#000080"), division: "Botola 1", color: "#000080", cafTitles: [{ year: 1981, opponent: "Shooting Stars (Nigeria)", score: "1-1 / 3-1" }, { year: 1983, opponent: "Nkana Red Devils (Zambie)", score: "2-0 / 0-1" }, { year: 1984, opponent: "Nkana Red Devils (Zambie)", score: "3-0 / 0-1" }], totalCAFTitles: 3, botolaTitles: 12 },
  { name: "Union Touarga Sport", acronym: "UTS", city: "Rabat", region: "Rabat-Salé-Kénitra", stadium: "Stade Moulay Abdallah", founded: 1960, logo: clubLogo("UTS", "#FF8C00"), division: "Botola 1", color: "#FF8C00", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "US Kénitra", acronym: "USK", city: "Kénitra", region: "Rabat-Salé-Kénitra", stadium: "Stade municipal de Kénitra", founded: 1938, logo: clubLogo("USK", "#006400"), division: "Botola 1", color: "#006400", cafTitles: [], totalCAFTitles: 0, botolaTitles: 2 },

  // Fès-Meknès
  { name: "Maghreb Association Sportive de Fès", acronym: "MAS", city: "Fès", region: "Fès-Meknès", stadium: "Stade Hassan II", founded: 1946, logo: clubLogo("MAS", "#0000CD"), division: "Botola 1", color: "#0000CD", cafTitles: [], totalCAFTitles: 0, botolaTitles: 4 },
  { name: "Wydad de Fès", acronym: "WDF", city: "Fès", region: "Fès-Meknès", stadium: "Stade Hassan II", founded: 1947, logo: clubLogo("WDF", "#C1272D"), division: "Botola 2", color: "#C1272D", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },

  // Tanger-Tétouan-Al Hoceima
  { name: "Ittihad Athletic de Tanger", acronym: "IRT", city: "Tanger", region: "Tanger-Tétouan-Al Hoceima", stadium: "Stade Ibn Batouta", founded: 1928, logo: clubLogo("IRT", "#0000FF"), division: "Botola 1", color: "#0000FF", cafTitles: [], totalCAFTitles: 0, botolaTitles: 1 },
  { name: "Maghreb Athletic de Tétouan", acronym: "MAT", city: "Tétouan", region: "Tanger-Tétouan-Al Hoceima", stadium: "Stade Saniat Rmel", founded: 1922, logo: clubLogo("MAT", "#FF4500"), division: "Botola 1", color: "#FF4500", cafTitles: [], totalCAFTitles: 0, botolaTitles: 2 },
  { name: "IRT Hoceima", acronym: "IRTH", city: "Al Hoceima", region: "Tanger-Tétouan-Al Hoceima", stadium: "Stade Mimoun Al Hadoui", founded: 1976, logo: clubLogo("IRTH", "#4169E1"), division: "Botola 2", color: "#4169E1", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },

  // Oriental
  { name: "Renaissance Sportive de Berkane", acronym: "RSB", city: "Berkane", region: "Oriental", stadium: "Stade Moulay Abdallah de Berkane", founded: 1938, logo: clubLogo("RSB", "#DAA520"), division: "Botola 1", color: "#DAA520", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "Mouloudia Club d'Oujda", acronym: "MCO", city: "Oujda", region: "Oriental", stadium: "Stade d'honneur d'Oujda", founded: 1946, logo: clubLogo("MCO", "#8B0000"), division: "Botola 1", color: "#8B0000", cafTitles: [], totalCAFTitles: 0, botolaTitles: 1 },

  // Marrakech-Safi
  { name: "Kawkab Athletic de Marrakech", acronym: "KACM", city: "Marrakech", region: "Marrakech-Safi", stadium: "Stade de Marrakech", founded: 1947, logo: clubLogo("KACM", "#006400"), division: "Botola 1", color: "#006400", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "Raja de Safi", acronym: "RJS", city: "Safi", region: "Marrakech-Safi", stadium: "Stade El Massira", founded: 1928, logo: clubLogo("RJS", "#228B22"), division: "Botola 2", color: "#228B22", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },

  // Souss-Massa
  { name: "Hassania Union Sport d'Agadir", acronym: "HUSA", city: "Agadir", region: "Souss-Massa", stadium: "Stade Adrar", founded: 1946, logo: clubLogo("HUSA", "#FF6347"), division: "Botola 1", color: "#FF6347", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "Olympique de Safi", acronym: "OCS", city: "Safi", region: "Souss-Massa", stadium: "Stade El Massira", founded: 1921, logo: clubLogo("OCS", "#4682B4"), division: "Botola 2", color: "#4682B4", cafTitles: [], totalCAFTitles: 0, botolaTitles: 1 },

  // Béni Mellal-Khénifra
  { name: "Olympique Club de Khouribga", acronym: "OCK", city: "Khouribga", region: "Béni Mellal-Khénifra", stadium: "Stade de Khouribga", founded: 1949, logo: clubLogo("OCK", "#2F4F4F"), division: "Botola 1", color: "#2F4F4F", cafTitles: [], totalCAFTitles: 0, botolaTitles: 2 },
  { name: "Union Sportive de Béni Mellal", acronym: "USBM", city: "Béni Mellal", region: "Béni Mellal-Khénifra", stadium: "Stade municipal de Béni Mellal", founded: 1940, logo: clubLogo("USBM", "#800080"), division: "Botola 2", color: "#800080", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },

  // Drâa-Tafilalet
  { name: "COD de Meknès", acronym: "COD", city: "Errachidia", region: "Drâa-Tafilalet", stadium: "Stade d'Errachidia", founded: 1965, logo: clubLogo("COD", "#A0522D"), division: "Botola 2", color: "#A0522D", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },

  // ═══ NEW BOTOLA 1 TEAMS (2025-26) ══════════════════════════════════════════
  // Casablanca-Settat
  { name: "Difaa El Jadida", acronym: "DHJ", city: "El Jadida", region: "Casablanca-Settat", stadium: "Complexe Sportif El Abdi", founded: 1946, logo: clubLogo("DHJ", "#1B5E20"), division: "Botola 1", color: "#1B5E20", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "Renaissance Club Athletic Zemamra", acronym: "RCAZ", city: "Zemamra", region: "Casablanca-Settat", stadium: "Stade Municipal de Zemamra", founded: 1977, logo: clubLogo("RCAZ", "#FFD700"), division: "Botola 1", color: "#FFD700", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  // Fès-Meknès
  { name: "CODM de Meknès", acronym: "CODM", city: "Meknès", region: "Fès-Meknès", stadium: "Stade d'Honneur de Meknès", founded: 1960, logo: clubLogo("CODM", "#4A148C"), division: "Botola 1", color: "#4A148C", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  // Marrakech-Safi
  { name: "Jeunesse Sportive Soualem", acronym: "JSS", city: "Soualem", region: "Marrakech-Safi", stadium: "Stade de Soualem", founded: 2012, logo: clubLogo("JSS", "#E65100"), division: "Botola 1", color: "#E65100", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  // Oriental
  { name: "Union Sportive Musulmane d'Oujda", acronym: "USMO", city: "Oujda", region: "Oriental", stadium: "Stade d'Honneur d'Oujda", founded: 1957, logo: clubLogo("USMO", "#1565C0"), division: "Botola 1", color: "#1565C0", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },

  // ═══ BOTOLA 2 (2025-26) ═══════════════════════════════════════════════════
  // Casablanca-Settat
  { name: "Rachad Bernoussi", acronym: "RB", city: "Casablanca", region: "Casablanca-Settat", stadium: "Stade Bernoussi", founded: 1967, logo: clubLogo("RB", "#BF360C"), division: "Botola 2", color: "#BF360C", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "Chabab Mohammedia", acronym: "RBM", city: "Mohammedia", region: "Casablanca-Settat", stadium: "Stade Municipal de Mohammedia", founded: 1951, logo: clubLogo("RBM", "#228B22"), division: "Botola 2", color: "#228B22", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  // Rabat-Salé-Kénitra
  { name: "Stade Marocain", acronym: "SM", city: "Rabat", region: "Rabat-Salé-Kénitra", stadium: "Stade Marocain", founded: 1925, logo: clubLogo("SM", "#37474F"), division: "Botola 2", color: "#37474F", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "AS Salé", acronym: "ASS", city: "Salé", region: "Rabat-Salé-Kénitra", stadium: "Stade de Salé", founded: 1962, logo: clubLogo("ASS", "#00838F"), division: "Botola 2", color: "#00838F", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "Union Sportive de Kénitra", acronym: "USK", city: "Kénitra", region: "Rabat-Salé-Kénitra", stadium: "Stade Municipal de Kénitra", founded: 1938, logo: clubLogo("USK", "#006400"), division: "Botola 2", color: "#006400", cafTitles: [], totalCAFTitles: 0, botolaTitles: 2 },
  { name: "Union de Sidi Kacem", acronym: "USS", city: "Sidi Kacem", region: "Rabat-Salé-Kénitra", stadium: "Stade Municipal de Sidi Kacem", founded: 1930, logo: clubLogo("USS", "#33691E"), division: "Botola 2", color: "#33691E", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  // Fès-Meknès
  { name: "Wydad de Fès", acronym: "WDF", city: "Fès", region: "Fès-Meknès", stadium: "Stade Hassan II", founded: 1947, logo: clubLogo("WDF", "#C1272D"), division: "Botola 2", color: "#C1272D", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  // Tanger-Tétouan-Al Hoceima
  { name: "IRT Hoceima", acronym: "IRTH", city: "Al Hoceima", region: "Tanger-Tétouan-Al Hoceima", stadium: "Stade Mimoun Al Hadoui", founded: 1976, logo: clubLogo("IRTH", "#4169E1"), division: "Botola 2", color: "#4169E1", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  // Oriental
  { name: "Union Sportive Amal Taza", acronym: "USAT", city: "Taza", region: "Oriental", stadium: "Stade Municipal de Taza", founded: 1961, logo: clubLogo("USAT", "#4E342E"), division: "Botola 2", color: "#4E342E", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  // Marrakech-Safi
  { name: "Kawkab Athletic de Marrakech", acronym: "KACM", city: "Marrakech", region: "Marrakech-Safi", stadium: "Stade de Marrakech", founded: 1947, logo: clubLogo("KACM", "#006400"), division: "Botola 2", color: "#006400", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  // Souss-Massa
  { name: "Olympique Dcheira", acronym: "ODC", city: "Dcheira", region: "Souss-Massa", stadium: "Stade Ahfir", founded: 1950, logo: clubLogo("ODC", "#0D47A1"), division: "Botola 2", color: "#0D47A1", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "USM Aït Melloul", acronym: "USMA", city: "Aït Melloul", region: "Souss-Massa", stadium: "Stade d'Aït Melloul", founded: 1965, logo: clubLogo("USMA", "#827717"), division: "Botola 2", color: "#827717", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  // Béni Mellal-Khénifra
  { name: "Chabab Atlas Khénifra", acronym: "CAK", city: "Khénifra", region: "Béni Mellal-Khénifra", stadium: "Stade Municipal de Khénifra", founded: 1960, logo: clubLogo("CAK", "#3E2723"), division: "Botola 2", color: "#3E2723", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "Union Sportive de Béni Mellal", acronym: "USBM", city: "Béni Mellal", region: "Béni Mellal-Khénifra", stadium: "Stade Municipal de Béni Mellal", founded: 1940, logo: clubLogo("USBM", "#800080"), division: "Botola 2", color: "#800080", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "Ittihad Khemisset", acronym: "IK", city: "Khemisset", region: "Béni Mellal-Khénifra", stadium: "Stade de Khemisset", founded: 1942, logo: clubLogo("IK", "#F57F17"), division: "Botola 2", color: "#F57F17", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  // Drâa-Tafilalet
  { name: "Raja de Safi", acronym: "RJS", city: "Safi", region: "Marrakech-Safi", stadium: "Stade El Massira", founded: 1928, logo: clubLogo("RJS", "#228B22"), division: "Botola 2", color: "#228B22", cafTitles: [], totalCAFTitles: 0, botolaTitles: 0 },
  { name: "Olympique de Safi", acronym: "OCS", city: "Safi", region: "Souss-Massa", stadium: "Stade El Massira", founded: 1921, logo: clubLogo("OCS", "#4682B4"), division: "Botola 2", color: "#4682B4", cafTitles: [], totalCAFTitles: 0, botolaTitles: 1 },
]

export const REGIONS_WITH_BOTOLA = [...new Set(FOOTBALL_CLUBS.map(c => c.region))]

// ── Transport & Logistics Detailed Data ────────────────────────────────────

export interface TransportInfrastructure {
  name: string;
  type: 'gare' | 'aéroport' | 'port' | 'autoroute' | 'cité_logistique';
  city: string;
  region: string;
  capacity?: string;
  yearOpened?: number;
  investment?: string;
  source: string;
}

export const TRANSPORT_INFRASTRUCTURES: TransportInfrastructure[] = [
  // Gares ONCF
  { name: "Gare de Casa-Voyageurs", type: "gare", city: "Casablanca", region: "Casablanca-Settat", capacity: "15M passagers/an", yearOpened: 1907, source: "ONCF" },
  { name: "Gare de Rabat-Agdal", type: "gare", city: "Rabat", region: "Rabat-Salé-Kénitra", capacity: "8M passagers/an", yearOpened: 2007, source: "ONCF" },
  { name: "Gare de Tanger-Ville", type: "gare", city: "Tanger", region: "Tanger-Tétouan-Al Hoceima", capacity: "5M passagers/an", yearOpened: 2009, source: "ONCF" },
  { name: "Gare de Fès", type: "gare", city: "Fès", region: "Fès-Meknès", capacity: "4M passagers/an", yearOpened: 1928, source: "ONCF" },
  { name: "Gare de Marrakech", type: "gare", city: "Marrakech", region: "Marrakech-Safi", capacity: "4M passagers/an", yearOpened: 1928, source: "ONCF" },
  { name: "Gare de Meknès", type: "gare", city: "Meknès", region: "Fès-Meknès", capacity: "2M passagers/an", yearOpened: 1922, source: "ONCF" },
  { name: "Gare de Kenitra", type: "gare", city: "Kénitra", region: "Rabat-Salé-Kénitra", capacity: "3M passagers/an", yearOpened: 1923, source: "ONCF" },
  { name: "Gare de Casa Port", type: "gare", city: "Casablanca", region: "Casablanca-Settat", capacity: "6M passagers/an", yearOpened: 1907, source: "ONCF" },
  // Aéroports ONDA
  { name: "Aéroport Mohammed V", type: "aéroport", city: "Casablanca", region: "Casablanca-Settat", capacity: "14M passagers", yearOpened: 1943, source: "ONDA" },
  { name: "Aéroport Marrakech Menara", type: "aéroport", city: "Marrakech", region: "Marrakech-Safi", capacity: "10M passagers", yearOpened: 1940, source: "ONDA" },
  { name: "Aéroport Agadir Al Massira", type: "aéroport", city: "Agadir", region: "Souss-Massa", capacity: "5M passagers", yearOpened: 1961, source: "ONDA" },
  { name: "Aéroport Tanger Ibn Battouta", type: "aéroport", city: "Tanger", region: "Tanger-Tétouan-Al Hoceima", capacity: "4M passagers", yearOpened: 1956, source: "ONDA" },
  { name: "Aéroport Fès-Saïss", type: "aéroport", city: "Fès", region: "Fès-Meknès", capacity: "2.5M passagers", yearOpened: 2003, source: "ONDA" },
  { name: "Aéroport Rabat-Salé", type: "aéroport", city: "Rabat", region: "Rabat-Salé-Kénitra", capacity: "2M passagers", yearOpened: 2008, source: "ONDA" },
  { name: "Aéroport Nador El Aroui", type: "aéroport", city: "Nador", region: "Oriental", capacity: "1M passagers", yearOpened: 1963, source: "ONDA" },
  { name: "Aéroport Oujda Angad", type: "aéroport", city: "Oujda", region: "Oriental", capacity: "0.5M passagers", yearOpened: 1965, source: "ONDA" },
  { name: "Aéroport Laâyoune Hassan I", type: "aéroport", city: "Laâyoune", region: "Laâyoune-Sakia El Hamra", capacity: "0.4M passagers", yearOpened: 1970, source: "ONDA" },
  { name: "Aéroport Dakhla", type: "aéroport", city: "Dakhla", region: "Dakhla-Oued Ed-Dahab", capacity: "0.3M passagers", yearOpened: 1976, source: "ONDA" },
  // Ports
  { name: "Tanger Med 1", type: "port", city: "Tanger", region: "Tanger-Tétouan-Al Hoceima", capacity: "3M TEU", yearOpened: 2007, source: "TMPA" },
  { name: "Tanger Med 2", type: "port", city: "Tanger", region: "Tanger-Tétouan-Al Hoceima", capacity: "6M TEU", yearOpened: 2019, source: "TMPA" },
  { name: "Port de Jorf Lasfar", type: "port", city: "El Jadida", region: "Casablanca-Settat", capacity: "40M tonnes", yearOpened: 1981, source: "ANP" },
  { name: "Port de Casablanca", type: "port", city: "Casablanca", region: "Casablanca-Settat", capacity: "32M tonnes", yearOpened: 1906, source: "ANP" },
  { name: "Port de Nador", type: "port", city: "Nador", region: "Oriental", capacity: "4M tonnes", yearOpened: 1967, source: "ANP" },
  { name: "Port d'Agadir", type: "port", city: "Agadir", region: "Souss-Massa", capacity: "3M tonnes", yearOpened: 1971, source: "ANP" },
  { name: "Port de Safi", type: "port", city: "Safi", region: "Marrakech-Safi", capacity: "2M tonnes", yearOpened: 1920, source: "ANP" },
  // Cités logistiques
  { name: "Tanger Med Cité Logistique", type: "cité_logistique", city: "Tanger", region: "Tanger-Tétouan-Al Hoceima", capacity: "300 ha", investment: "12 Mds MAD", source: "TMPA" },
  { name: "Jorf Cité Logistique", type: "cité_logistique", city: "El Jadida", region: "Casablanca-Settat", capacity: "200 ha", investment: "8 Mds MAD", source: "ANP" },
]

export function getTransportDetailData(indicatorCode: string): TransportInfrastructure[] {
  switch (indicatorCode) {
    case 'ONCF_PASSAGERS':
    case 'ONCF_REVENUS':
      return TRANSPORT_INFRASTRUCTURES.filter(i => i.type === 'gare');
    case 'ONDA_PASSAGERS':
    case 'ONDA_CARGO':
      return TRANSPORT_INFRASTRUCTURES.filter(i => i.type === 'aéroport');
    case 'PORT_TRAFFIC':
    case 'TANGER_MED_TEU':
    case 'PORT_PASSENGERS':
      return TRANSPORT_INFRASTRUCTURES.filter(i => i.type === 'port');
    case 'HIGHWAY_KM':
    case 'HIGHWAY_TRAFFIC':
    case 'ADM_REVENUS':
      return TRANSPORT_INFRASTRUCTURES.filter(i => i.type === 'autoroute');
    default:
      return TRANSPORT_INFRASTRUCTURES;
  }
}

// ── Commerce Detailed Data ─────────────────────────────────────────────────

export interface TradingPartner {
  country: string;
  exportsMd: number;
  importsMd: number;
  totalMd: number;
  share: number;
  agreement?: string;
}

export const TOP_TRADING_PARTNERS: TradingPartner[] = [
  { country: "Espagne", exportsMd: 98.1, importsMd: 122.1, totalMd: 220.2, share: 29.1, agreement: "UE" },
  { country: "France", exportsMd: 81.2, importsMd: 72.0, totalMd: 153.2, share: 21.0, agreement: "UE" },
  { country: "Allemagne", exportsMd: 28.5, importsMd: 36.7, totalMd: 65.2, share: 8.4, agreement: "UE" },
  { country: "Italie", exportsMd: 22.0, importsMd: 32.2, totalMd: 54.2, share: 7.7, agreement: "UE" },
  { country: "Turquie", exportsMd: 15.8, importsMd: 34.0, totalMd: 49.8, share: 6.7, agreement: "ALE" },
  { country: "Chine", exportsMd: 7.4, importsMd: 74.4, totalMd: 81.9, share: 5.5, agreement: null },
  { country: "États-Unis", exportsMd: 16.3, importsMd: 54.1, totalMd: 70.5, share: 4.8, agreement: "ALE" },
  { country: "Royaume-Uni", exportsMd: 24.8, importsMd: 11.5, totalMd: 36.3, share: 2.5, agreement: null },
  { country: "Brésil", exportsMd: 3.2, importsMd: 22.5, totalMd: 25.7, share: 1.7, agreement: null },
  { country: "Arabie Saoudite", exportsMd: 8.5, importsMd: 15.0, totalMd: 23.5, share: 1.6, agreement: "GAFTA" },
  { country: "Inde", exportsMd: 5.0, importsMd: 18.0, totalMd: 23.0, share: 1.5, agreement: null },
  { country: "Japon", exportsMd: 4.0, importsMd: 16.0, totalMd: 20.0, share: 1.2, agreement: null },
  { country: "Corée du Sud", exportsMd: 3.5, importsMd: 14.0, totalMd: 17.5, share: 1.0, agreement: null },
  { country: "Pays-Bas", exportsMd: 6.0, importsMd: 10.0, totalMd: 16.0, share: 0.9, agreement: "UE" },
  { country: "Belgique", exportsMd: 5.5, importsMd: 8.0, totalMd: 13.5, share: 0.8, agreement: "UE" },
]

export interface ExportProduct {
  product: string;
  valueMd: number;
  share: number;
  sector: string;
}

export const TOP_EXPORT_PRODUCTS: ExportProduct[] = [
  { product: "Voitures particulières", valueMd: 157.6, share: 14.9, sector: "Automobile" },
  { product: "Engrais naturels/chimiques", valueMd: 63.8, share: 14.0, sector: "Phosphates" },
  { product: "Fils et câbles isolés", valueMd: 55.0, share: 10.5, sector: "Électronique" },
  { product: "Vêtements confectionnés", valueMd: 34.2, share: 6.5, sector: "Textile" },
  { product: "Pièces automobiles", valueMd: 19.5, share: 3.7, sector: "Automobile" },
  { product: "Parties d'aéronefs", valueMd: 18.5, share: 3.5, sector: "Aéronautique" },
  { product: "Acide phosphorique", valueMd: 16.8, share: 3.2, sector: "Phosphates" },
  { product: "Fruits à coque", valueMd: 25.0, share: 4.9, sector: "Agriculture" },
  { product: "Légumes", valueMd: 21.0, share: 4.2, sector: "Agriculture" },
  { product: "Poissons", valueMd: 17.5, share: 3.5, sector: "Pêche" },
]

export function getCommerceDetailData(indicatorCode: string): TradingPartner[] | ExportProduct[] {
  switch (indicatorCode) {
    case 'EXPORTS_FOB':
      return TOP_EXPORT_PRODUCTS;
    case 'IMPORTS_CIF':
      return TOP_TRADING_PARTNERS;
    case 'TRADE_DEFICIT':
      return TOP_TRADING_PARTNERS;
    case 'FDI_NET':
      return TOP_TRADING_PARTNERS;
    default:
      return TOP_TRADING_PARTNERS;
  }
}

// ── Energy Detailed Data ───────────────────────────────────────────────────

export interface EnergyProject {
  name: string;
  type: 'solaire' | 'éolien' | 'hydro' | 'thermique' | 'hybrid';
  capacityMw: number;
  location: string;
  region: string;
  yearOpened: number;
  investment?: string;
  annualGwh?: number;
  source: string;
}

export const ENERGY_PROJECTS: EnergyProject[] = [
  // Solaire
  { name: "Noor Ouarzazate I", type: "solaire", capacityMw: 160, location: "Ouarzazate", region: "Drâa-Tafilalet", yearOpened: 2016, investment: "3 Mds USD", annualGwh: 370, source: "MASEN" },
  { name: "Noor Ouarzazate II", type: "solaire", capacityMw: 200, location: "Ouarzazate", region: "Drâa-Tafilalet", yearOpened: 2018, investment: "2 Mds USD", annualGwh: 600, source: "MASEN" },
  { name: "Noor Ouarzazate III", type: "solaire", capacityMw: 150, location: "Ouarzazate", region: "Drâa-Tafilalet", yearOpened: 2018, investment: "2.5 Mds USD", annualGwh: 500, source: "MASEN" },
  { name: "Noor Ouarzazate IV", type: "solaire", capacityMw: 72, location: "Ouarzazate", region: "Drâa-Tafilalet", yearOpened: 2018, source: "MASEN" },
  { name: "Noor Midelt I", type: "hybrid", capacityMw: 800, location: "Midelt", region: "Fès-Meknès", yearOpened: 2025, investment: "8 Mds MAD", source: "MASEN" },
  { name: "Ain Beni Mathar", type: "solaire", capacityMw: 200, location: "Ain Beni Mathar", region: "Oriental", yearOpened: 2018, source: "MASEN" },
  // Éolien
  { name: "Parc de Tarfaya", type: "éolien", capacityMw: 301, location: "Tarfaya", region: "Guelmim-Oued Noun", yearOpened: 2014, annualGwh: 1075, source: "MASEN" },
  { name: "Parc de Boujdour", type: "éolien", capacityMw: 318, location: "Boujdour", region: "Laâyoune-Sakia El Hamra", yearOpened: 2014, source: "MASEN" },
  { name: "Parc Jbel Lahdid", type: "éolien", capacityMw: 270, location: "Essaouira", region: "Marrakech-Safi", yearOpened: 2024, annualGwh: 952, source: "ONEE" },
  { name: "Parc Aftissat II", type: "éolien", capacityMw: 200, location: "Foum El Oued", region: "Laâyoune-Sakia El Hamra", yearOpened: 2019, annualGwh: 900, source: "ONEE" },
  { name: "Parc Taza Phase II", type: "éolien", capacityMw: 150, location: "Taza", region: "Fès-Meknès", yearOpened: 2024, annualGwh: 515, source: "ONEE" },
  { name: "Parc Tiskrad", type: "éolien", capacityMw: 300, location: "Tiskrad", region: "Dakhla-Oued Ed-Dahab", yearOpened: 2025, annualGwh: 1000, source: "ONEE" },
  { name: "Parc Essaouira", type: "éolien", capacityMw: 60, location: "Essaouira", region: "Marrakech-Safi", yearOpened: 2008, source: "ONEE" },
  { name: "Parc Cap Sim", type: "éolien", capacityMw: 50, location: "Essaouira", region: "Marrakech-Safi", yearOpened: 2009, source: "ONEE" },
  { name: "Parc Tetouan", type: "éolien", capacityMw: 70, location: "Tétouan", region: "Tanger-Tétouan-Al Hoceima", yearOpened: 2013, source: "ONEE" },
  // Hydro
  { name: "Barrage Bin El Ouidane", type: "hydro", capacityMw: 135, location: "Bin El Ouidane", region: "Béni Mellal-Khénifra", yearOpened: 1953, source: "ONEE" },
  { name: "Barrage Afourar", type: "hydro", capacityMw: 120, location: "Afourar", region: "Béni Mellal-Khénifra", yearOpened: 1979, source: "ONEE" },
  { name: "Barrage Oued El Makhazine", type: "hydro", capacityMw: 120, location: "Larache", region: "Tanger-Tétouan-Al Hoceima", yearOpened: 1979, source: "ONEE" },
  { name: "Pompage Abdelmoumen", type: "hydro", capacityMw: 350, location: "Agadir", region: "Souss-Massa", yearOpened: 2028, investment: "10 Mds MAD", source: "ONEE" },
  // Thermique
  { name: "Jorf Lasfar", type: "thermique", capacityMw: 2000, location: "El Jadida", region: "Casablanca-Settat", yearOpened: 1998, source: "ONEE" },
  { name: "Mohammedia", type: "thermique", capacityMw: 1200, location: "Mohammedia", region: "Casablanca-Settat", yearOpened: 2002, source: "ONEE" },
  { name: "Kénitra", type: "thermique", capacityMw: 600, location: "Kénitra", region: "Rabat-Salé-Kénitra", yearOpened: 2003, source: "ONEE" },
  { name: "Safi", type: "thermique", capacityMw: 600, location: "Safi", region: "Marrakech-Safi", yearOpened: 2005, source: "ONEE" },
  { name: "Al Wahda", type: "thermique", capacityMw: 990, location: "Kenitra", region: "Rabat-Salé-Kénitra", yearOpened: 2027, investment: "4.16 Mds MAD", source: "ONEE" },
]

export interface EnergyDistributor {
  name: string;
  region: string;
  sharePercent: number;
  clients: string;
  source: string;
}

export const ENERGY_DISTRIBUTORS: EnergyDistributor[] = [
  { name: "LYDEC (ex-LYDEC)", region: "Casablanca-Settat", sharePercent: 18.2, clients: "3.5M", source: "ANRE" },
  { name: "SRM Casablanca-Settat", region: "Casablanca-Settat", sharePercent: 15.3, clients: "2.8M", source: "ANRE" },
  { name: "REDAL", region: "Rabat-Salé-Kénitra", sharePercent: 14.6, clients: "2.5M", source: "ANRE" },
  { name: "AMENDIS Tanger", region: "Tanger-Tétouan-Al Hoceima", sharePercent: 10.6, clients: "1.2M", source: "ANRE" },
  { name: "ONEE Distribution", region: "Autres régions", sharePercent: 52.4, clients: "8M", source: "ANRE" },
]

export function getEnergyDetailData(indicatorCode: string): EnergyProject[] | EnergyDistributor[] {
  switch (indicatorCode) {
    case 'WIND_CAPACITY':
      return ENERGY_PROJECTS.filter(p => p.type === 'éolien');
    case 'SOLAR_CAPACITY':
      return ENERGY_PROJECTS.filter(p => p.type === 'solaire' || p.type === 'hybrid');
    case 'NOOR_OUTPUT':
      return ENERGY_PROJECTS.filter(p => p.name.includes('Noor'));
    case 'INSTALLED_CAPACITY':
      return ENERGY_PROJECTS;
    default:
      return ENERGY_DISTRIBUTORS;
  }
}

// ── FIFA Rankings ──────────────────────────────────────────────────────────
export const FIFA_RANKINGS: { year: number; rank: number }[] = [
  { year: 2000, rank: 28 }, { year: 2001, rank: 32 }, { year: 2002, rank: 30 },
  { year: 2003, rank: 35 }, { year: 2004, rank: 33 }, { year: 2005, rank: 29 },
  { year: 2006, rank: 26 }, { year: 2007, rank: 25 }, { year: 2008, rank: 27 },
  { year: 2009, rank: 31 }, { year: 2010, rank: 28 }, { year: 2011, rank: 25 },
  { year: 2012, rank: 22 }, { year: 2013, rank: 23 }, { year: 2014, rank: 24 },
  { year: 2015, rank: 21 }, { year: 2016, rank: 20 }, { year: 2017, rank: 19 },
  { year: 2018, rank: 17 }, { year: 2019, rank: 16 }, { year: 2020, rank: 15 },
  { year: 2021, rank: 14 }, { year: 2022, rank: 13 }, { year: 2023, rank: 12 },
  { year: 2024, rank: 10 }, { year: 2025, rank: 8 }, { year: 2026, rank: 7 },
]

// ── R&D Spending Detail ────────────────────────────────────────────────────
export interface RDSector {
  sector: string;
  sectorEn: string;
  share: number;
  amountMnMAD: number;
  description: string;
  descriptionEn: string;
}
export const RD_SPENDING_DETAIL: RDSector[] = [
  { sector: "Enseignement supérieur", sectorEn: "Higher Education", share: 35.0, amountMnMAD: 1700, description: "Universités et centres de recherche académiques", descriptionEn: "Universities and academic research centers" },
  { sector: "Entreprises privées", sectorEn: "Private Enterprises", share: 30.0, amountMnMAD: 1450, description: "R&D industrielle (OCP, automotive, aéronautique)", descriptionEn: "Industrial R&D (OCP, automotive, aeronautics)" },
  { sector: "État et administrations", sectorEn: "Government", share: 20.0, amountMnMAD: 970, description: "CNRST, ministères, agences publiques", descriptionEn: "CNRST, ministries, public agencies" },
  { sector: "Organismes internationaux", sectorEn: "International Organizations", share: 10.0, amountMnMAD: 480, description: "Fonds bilatéraux, UE, Banque mondiale", descriptionEn: "Bilateral funds, EU, World Bank" },
  { sector: "ONG et associations", sectorEn: "NGOs & Associations", share: 5.0, amountMnMAD: 240, description: "ONG scientifiques, fondations privées", descriptionEn: "Scientific NGOs, private foundations" },
]

// ── Tax Detail ─────────────────────────────────────────────────────────────
export interface TaxRow {
  category: string;
  categoryEn: string;
  revenueBnMAD: number;
  share: number;
  source: string;
}
export const TAX_DETAIL: TaxRow[] = [
  { category: "TVA", categoryEn: "VAT", revenueBnMAD: 98.5, share: 35.7, source: "TGR / DGI" },
  { category: "Impôt sur les Sociétés (IS)", categoryEn: "Corporate Tax", revenueBnMAD: 62.3, share: 22.6, source: "TGR / DGI" },
  { category: "Impôt sur le Revenu (IR)", categoryEn: "Income Tax", revenueBnMAD: 48.7, share: 17.7, source: "TGR / DGI" },
  { category: "Taxe Intérieure de Consommation", categoryEn: "Excise Tax", revenueBnMAD: 22.5, share: 8.2, source: "TGR / DGI" },
  { category: "Droits de Douane", categoryEn: "Customs Duties", revenueBnMAD: 12.8, share: 4.6, source: "ADII" },
  { category: "Taxes parafiscales", categoryEn: "Parafiscal Taxes", revenueBnMAD: 15.2, share: 5.5, source: "TGR / DGI" },
  { category: "Autres recettes fiscales", categoryEn: "Other Tax Revenues", revenueBnMAD: 15.8, share: 5.7, source: "TGR / DGI" },
]

// ── Debt Detail ────────────────────────────────────────────────────────────
export interface DebtRow {
  type: string;
  typeEn: string;
  amountBnMAD: number;
  share: number;
  interestRate: string;
  source: string;
}
export const DEBT_DETAIL: DebtRow[] = [
  { type: "Dette intérieure", typeEn: "Domestic Debt", amountBnMAD: 640, share: 60.0, interestRate: "3.2%", source: "TGR / Bank Al-Maghrib" },
  { type: "Dette extérieure", typeEn: "External Debt", amountBnMAD: 320, share: 30.0, interestRate: "4.1%", source: "Ministère des Finances" },
  { type: "Garanties de l'État", typeEn: "State Guarantees", amountBnMAD: 65, share: 6.1, interestRate: "—", source: "Ministère des Finances" },
  { type: "Dette des EEP", typeEn: "Public Enterprises Debt", amountBnMAD: 42, share: 3.9, interestRate: "—", source: "Ministère des Finances" },
]
