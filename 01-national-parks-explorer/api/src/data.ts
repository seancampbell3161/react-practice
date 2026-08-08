export interface ParkSummary {
  id: string;
  name: string;
  state: string;
  tagline: string;
}

export interface ParkDetail extends ParkSummary {
  description: string;
  established: string;
  sizeAcres: number;
  activities: string[];
}

export const PARKS: ParkDetail[] = [
  {
    id: 'yellowstone',
    name: 'Yellowstone',
    state: 'WY, MT, ID',
    tagline: "America's first national park",
    description:
      'A vast wilderness sitting atop a volcanic hot spot, famous for its geysers, hot springs, and abundant wildlife including bison, wolves, and grizzly bears.',
    established: '1872',
    sizeAcres: 2219791,
    activities: ['Hiking', 'Wildlife watching', 'Geysers', 'Camping'],
  },
  {
    id: 'yosemite',
    name: 'Yosemite',
    state: 'CA',
    tagline: 'Granite cliffs and giant sequoias',
    description:
      'Known for its waterfalls, deep valleys, and towering granite monoliths like El Capitan and Half Dome.',
    established: '1890',
    sizeAcres: 761748,
    activities: ['Rock climbing', 'Hiking', 'Waterfalls', 'Stargazing'],
  },
  {
    id: 'grand-canyon',
    name: 'Grand Canyon',
    state: 'AZ',
    tagline: 'A mile-deep canyon carved by the Colorado River',
    description:
      'One of the most dramatic landscapes on Earth, stretching 277 miles long and up to 18 miles wide.',
    established: '1919',
    sizeAcres: 1201647,
    activities: ['Hiking', 'Rafting', 'Mule rides', 'Sunset viewing'],
  },
  {
    id: 'zion',
    name: 'Zion',
    state: 'UT',
    tagline: 'Towering red sandstone cliffs',
    description:
      'Home to narrow slot canyons, the Virgin River, and dramatic sandstone cliffs in shades of red and cream.',
    established: '1919',
    sizeAcres: 147242,
    activities: ['Canyoneering', 'Hiking', 'Rock climbing'],
  },
  {
    id: 'acadia',
    name: 'Acadia',
    state: 'ME',
    tagline: 'Rocky Atlantic coastline and granite peaks',
    description:
      'The first national park east of the Mississippi, featuring rugged coastline, woodlands, and Cadillac Mountain.',
    established: '1916',
    sizeAcres: 49076,
    activities: ['Hiking', 'Biking', 'Tide pooling', 'Stargazing'],
  },
  {
    id: 'glacier',
    name: 'Glacier',
    state: 'MT',
    tagline: 'Pristine wilderness with ancient glaciers',
    description:
      'Known as the "Crown of the Continent," with rugged peaks, pristine lakes, and the historic Going-to-the-Sun Road.',
    established: '1910',
    sizeAcres: 1013322,
    activities: ['Hiking', 'Wildlife watching', 'Boating'],
  },
  {
    id: 'everglades',
    name: 'Everglades',
    state: 'FL',
    tagline: 'Subtropical wetlands teeming with wildlife',
    description:
      'A vast river of grass home to alligators, manatees, and hundreds of bird species.',
    established: '1934',
    sizeAcres: 1508538,
    activities: ['Canoeing', 'Wildlife watching', 'Airboat tours'],
  },
  {
    id: 'denali',
    name: 'Denali',
    state: 'AK',
    tagline: "Home to North America's tallest peak",
    description:
      'Six million acres of wild land surrounding Denali, which rises over 20,000 feet above sea level.',
    established: '1917',
    sizeAcres: 6028091,
    activities: ['Mountaineering', 'Wildlife watching', 'Hiking'],
  },
  {
    id: 'great-smoky-mountains',
    name: 'Great Smoky Mountains',
    state: 'TN, NC',
    tagline: 'The most visited national park in the US',
    description:
      'Ancient mountains cloaked in mist, with the highest biodiversity of any national park in the country.',
    established: '1934',
    sizeAcres: 522427,
    activities: ['Hiking', 'Wildlife watching', 'Fall foliage'],
  },
  {
    id: 'rocky-mountain',
    name: 'Rocky Mountain',
    state: 'CO',
    tagline: 'Alpine tundra above 14,000 feet',
    description:
      'A high-altitude landscape of jagged peaks, alpine lakes, and Trail Ridge Road, the highest paved road in the US.',
    established: '1915',
    sizeAcres: 265807,
    activities: ['Hiking', 'Wildlife watching', 'Scenic drives'],
  },
  {
    id: 'joshua-tree',
    name: 'Joshua Tree',
    state: 'CA',
    tagline: 'Where two deserts meet',
    description:
      'A surreal desert landscape where the Mojave and Colorado deserts converge, dotted with twisted Joshua trees and boulder piles.',
    established: '1994',
    sizeAcres: 795156,
    activities: ['Rock climbing', 'Stargazing', 'Hiking'],
  },
  {
    id: 'olympic',
    name: 'Olympic',
    state: 'WA',
    tagline: 'Rainforests, coastline, and mountains in one park',
    description:
      'Three distinct ecosystems in one park: glaciated mountains, old-growth temperate rainforest, and rugged Pacific coastline.',
    established: '1938',
    sizeAcres: 922650,
    activities: ['Hiking', 'Tide pooling', 'Camping'],
  },
];
