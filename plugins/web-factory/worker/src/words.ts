/**
 * Passphrase wordlist and generator.
 *
 * Generates 4-word passphrases like "coral-sunset-tide-2026"
 * using crypto.getRandomValues() for secure randomness.
 */

const WORDS = [
  // Nature
  "ocean", "river", "mountain", "forest", "meadow", "canyon", "valley", "island",
  "lagoon", "glacier", "desert", "prairie", "tundra", "reef", "marsh", "grove",
  "summit", "ridge", "creek", "brook", "spring", "falls", "cliff", "shore",
  "coast", "harbor", "cove", "dune", "bluff", "mesa", "plateau", "basin",
  // Weather & sky
  "storm", "breeze", "thunder", "lightning", "aurora", "rainbow", "cloud", "mist",
  "frost", "dew", "haze", "fog", "dawn", "dusk", "twilight", "eclipse",
  "zenith", "horizon", "north", "south", "east", "west", "solar", "lunar",
  // Colors
  "coral", "amber", "ivory", "scarlet", "crimson", "azure", "cobalt", "indigo",
  "violet", "mauve", "copper", "bronze", "silver", "golden", "onyx", "jade",
  "ruby", "pearl", "opal", "topaz", "slate", "sage", "teal", "cyan",
  "magenta", "sienna", "umber", "ochre", "rust", "cream", "blush", "plum",
  // Water
  "tide", "wave", "current", "ripple", "cascade", "rapids", "surf", "swell",
  "eddy", "whirl", "geyser", "delta", "fjord", "strait", "channel", "shoal",
  // Flora
  "cedar", "maple", "willow", "birch", "aspen", "cypress", "elm", "sequoia",
  "pine", "spruce", "oak", "laurel", "ivy", "fern", "moss", "lotus",
  "orchid", "lily", "dahlia", "jasmine", "iris", "violet", "daisy", "tulip",
  "poppy", "clover", "sage", "basil", "thyme", "mint", "rosemary", "lavender",
  // Fauna
  "falcon", "hawk", "eagle", "raven", "heron", "crane", "swift", "sparrow",
  "dove", "robin", "wren", "finch", "lark", "owl", "osprey", "condor",
  "wolf", "fox", "lynx", "bear", "stag", "otter", "seal", "whale",
  "dolphin", "salmon", "trout", "pike", "bass", "carp", "perch", "marlin",
  // Earth & minerals
  "granite", "marble", "quartz", "basalt", "flint", "shale", "obsidian", "agate",
  "jasper", "garnet", "crystal", "geode", "fossil", "ember", "spark", "flame",
  // Objects & materials
  "anchor", "compass", "lantern", "beacon", "prism", "lens", "mirror", "bell",
  "drum", "loom", "anvil", "forge", "kiln", "helm", "mast", "sail",
  "canvas", "linen", "silk", "velvet", "timber", "stone", "steel", "glass",
  // Actions & qualities
  "swift", "bold", "keen", "bright", "calm", "clear", "crisp", "deep",
  "fair", "firm", "free", "grand", "kind", "pure", "rare", "true",
  "warm", "wise", "brave", "noble", "steady", "gentle", "vivid", "serene",
  // Abstract
  "echo", "drift", "bloom", "crest", "pulse", "chord", "tempo", "rhythm",
  "verse", "cipher", "orbit", "nexus", "apex", "vertex", "arc", "spiral",
  // Time & seasons
  "spring", "summer", "autumn", "winter", "solstice", "equinox", "harvest", "frost",
  // Celestial
  "star", "comet", "meteor", "nova", "nebula", "cosmos", "astral", "stellar",
  "lunar", "solar", "zenith", "nadir", "corona", "halo", "orbit", "flux",
  // Terrain features
  "arch", "bridge", "pass", "gate", "tower", "spire", "dome", "vault",
  "terrace", "garden", "plaza", "court", "atrium", "alcove", "niche", "hall",
];

/**
 * Generate a passphrase: 3 random words + 4-digit number, joined with hyphens.
 * Example: "coral-sunset-tide-2026"
 */
export function generatePassphrase(): string {
  const arr = new Uint32Array(4);
  crypto.getRandomValues(arr);

  const words: string[] = [];
  for (let i = 0; i < 3; i++) {
    words.push(WORDS[arr[i] % WORDS.length]);
  }

  const num = 1000 + (arr[3] % 9000); // 1000–9999
  words.push(String(num));

  return words.join("-");
}
