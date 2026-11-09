const kebabCase = (str) => str.trim().toLowerCase().replace(/\s+/g, "-");

const createTextInput = ({ container, label, tooltip = null }) => {
  const template = document.querySelector("#textinput-template");
  const clone = template.content.cloneNode(true);

  const labelElement = clone.querySelector(".input-label");
  const tooltipElement = clone.querySelector(".input-tooltip");
  const input = clone.querySelector("input");

  labelElement.textContent = label;
  input.name = label === "Player" ? "player_name" : kebabCase(label);
  input.required = label === "Name" || label === "Player";

  if (tooltip) {
    tooltipElement.textContent = "ⓘ";
    tooltipElement.title = tooltip;
    tooltipElement.style.display = "inline";
  }

  document.querySelector(container).appendChild(clone);
};

const createValueInput = ({ container, label, tooltip, hasSpecialty = false }) => {
  const template = document.querySelector("#valueinput-template");
  const clone = template.content.cloneNode(true);

  const labelElement = clone.querySelector(".stat-label");
  const specialtyInput = clone.querySelector(".specialty-input");
  const statInput = clone.querySelector(".stat-input");

  labelElement.textContent = label;
  labelElement.title = tooltip;

  let category = null;

  if (container.includes("physical")) {
    category = "physical";
  } else if (container.includes("social")) {
    category = "social";
  } else if (container.includes("mental")) {
    category = "mental";
  }

  if (hasSpecialty) {
    specialtyInput.name = `${kebabCase(label)}-specialty`;
    statInput.classList.add("ability-input");
  } else {
    specialtyInput.remove();

    if (category) {
      statInput.classList.add("attr-input");
      statInput.dataset.category = category;
    }
  }

  statInput.name = kebabCase(label);
  statInput.id = `stat-${kebabCase(label)}`;
  statInput.type = "number";
  statInput.min = container.includes("abilities") ? 0 : 1;
  statInput.max = label === "Willpower" ? 10 : 5;
  statInput.value = label === "Willpower" ? 5 : label === "Essence" ? 2 : statInput.min;

  document.querySelector(container).appendChild(clone);
};

const createSelectInput = ({ container, label, options, tooltip = null, id = null }) => {
  const template = document.querySelector("#selectinput-template");
  const clone = template.content.cloneNode(true);

  const labelElement = clone.querySelector(".input-label");
  const tooltipElement = clone.querySelector(".input-tooltip");
  const select = clone.querySelector("select");

  labelElement.textContent = label;
  select.name = kebabCase(label);

  if (id) {
    select.id = id;
  }

  if (tooltip) {
    tooltipElement.title = tooltip;
    tooltipElement.style.display = "inline";
  }

  options.forEach(({ value, text }) => {
    select.add(new Option(text, value));
  });

  document.querySelector(container).appendChild(clone);
};

// Characteristics stats
const createCharacteristicsInputs = ([label, tooltip = null, container = "#bio-info"]) =>
  createTextInput({ container, label, tooltip });

[["Name"], ["Player"]].forEach(createCharacteristicsInputs);

createSelectInput({
  container: "#bio-info",
  label: "Caste",
  id: "caste-select",
  tooltip: "Your role chosen by the Unconquered Sun.",
  options: [
    { value: "Dawn", text: "Dawn (Warrior)" },
    { value: "Zenith", text: "Zenith (Priest/Leader)" },
    { value: "Twilight", text: "Twilight (Scholar/Sorcerer)" },
    { value: "Night", text: "Night (Spy/Assassin)" },
    { value: "Eclipse", text: "Eclipse (Ambassador)" },
  ],
});

[
  ["Concept"],
  ["Nature", "Your character's true personality archetype."],
  ["Anima", "The blazing iconic display of your Essence."],
].forEach(createCharacteristicsInputs);

// Attributes stats
const createAttributesInputs = ([container, label, tooltip]) =>
  createValueInput({ container, label, tooltip });

[
  ["#physical-attributes", "Strength", "Raw physical power."],
  ["#physical-attributes", "Dexterity", "Agility, speed, and grace."],
  ["#physical-attributes", "Stamina", "Physical resilience and health."],
  ["#social-attributes", "Charisma", "Charm and force of personality."],
  ["#social-attributes", "Manipulation", "Ability to influence and deceive."],
  ["#social-attributes", "Appearance", "Physical attractiveness."],
  ["#mental-attributes", "Perception", "Awareness and noticing details."],
  ["#mental-attributes", "Intelligence", "Raw intellect and memory."],
  ["#mental-attributes", "Wits", "Quick thinking and reaction time."],
  ["#core-traits", "Willpower", "Mental fortitude."],
  ["#core-traits", "Essence", "Raw magical power."],
  ["#virtues-advantages", "Compassion", "Empathy for the suffering."],
  ["#virtues-advantages", "Conviction", "Dedication to beliefs."],
  ["#virtues-advantages", "Temperance", "Self-control and moderation."],
  ["#virtues-advantages", "Valor", "Bravery in the face of danger."],
].forEach(createAttributesInputs);

// Abilities stats
const createAbilitiesInputs = ([container, label, tooltip, hasSpecialty = true]) =>
  createValueInput({ container, label, tooltip, hasSpecialty });

[
  ["#dawn-abilities", "Archery", "Bows and ranged weapons."],
  ["#dawn-abilities", "Brawl", "Unarmed combat."],
  ["#dawn-abilities", "Martial Arts", "Formalized unarmed fighting styles."],
  ["#dawn-abilities", "Thrown", "Swords, spears, and hand weapons."],
  ["#dawn-abilities", "Melee", "Knives and thrown projectiles."],
  ["#zenith-abilities", "Endurance", "Resisting fatigue and hardship."],
  ["#zenith-abilities", "Performance", "Art, music, and public speaking."],
  ["#zenith-abilities", "Presence", "Intimidation and commanding attention."],
  ["#zenith-abilities", "Resistance", "Withstanding poison and disease."],
  ["#zenith-abilities", "Survival", "Living off the land."],
  ["#twilight-abilities", "Craft", "Creating objects and art."],
  ["#twilight-abilities", "Investigation", "Finding clues and deducing facts."],
  ["#twilight-abilities", "Lore", "Academic and historical knowledge."],
  ["#twilight-abilities", "Medicine", "Healing and anatomy."],
  ["#twilight-abilities", "Occult", "Knowledge of spirits and magic."],
  ["#night-abilities", "Athletics", "Jumping, running, and acrobatics."],
  ["#night-abilities", "Awareness", "Noticing the hidden or stealthy."],
  ["#night-abilities", "Dodge", "Evading attacks."],
  ["#night-abilities", "Larceny", "Lockpicking, stealing, and crime."],
  ["#night-abilities", "Stealth", "Hiding and moving silently."],
  ["#eclipse-abilities", "Bureaucracy", "Navigating organizations and trade."],
  ["#eclipse-abilities", "Linguistics", "Knowing multiple languages."],
  ["#eclipse-abilities", "Ride", "Handling horses and beasts."],
  ["#eclipse-abilities", "Sail", "Piloting ships."],
  ["#eclipse-abilities", "Socialize", "Understanding cultural norms and manners."],
].forEach(createAbilitiesInputs);

// Final setups
const statWillpower = document.querySelector("#stat-willpower");
statWillpower.max = 10;
statWillpower.value = 5;

document.querySelector("#stat-essence").value = 2;
document.querySelectorAll("#virtues-advantages input").forEach((input) => {
  input.value = 1;
});

document.addEventListener("DOMContentLoaded", function () {
  // Initialize Tooltips
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // --- SINGLE SOURCE OF TRUTH FOR PRIORITIES ---
  const priorityDefinitions = [
    { label: "Primary", points: 8 },
    { label: "Secondary", points: 6 },
    { label: "Tertiary", points: 4 },
  ];

  const prioritySelects = document.querySelectorAll(".priority-select");
  const attrInputs = document.querySelectorAll(".attr-input");

  // Inject the options into the dropdowns on load
  prioritySelects.forEach((select) => {
    priorityDefinitions.forEach((def) => {
      let opt = document.createElement("option");
      opt.value = def.points;
      opt.textContent = `${def.label} (${def.points} Points)`;
      select.appendChild(opt);
    });
  });

  function updatePriorities() {
    let selectedValues = Array.from(prioritySelects)
      .map((s) => s.value)
      .filter((val) => val !== "");

    prioritySelects.forEach((s) => {
      let currentVal = s.value;
      Array.from(s.options).forEach((opt) => {
        if (opt.value !== "") {
          opt.disabled = selectedValues.includes(opt.value) && opt.value !== currentVal;
        }
      });

      let cat = s.dataset.category;
      let max = parseInt(s.value) || 0;
      document.getElementById(cat + "-max").innerText = max;
      recalculatePoints(cat, max);
    });
  }

  function recalculatePoints(category, max) {
    let categoryInputs = document.querySelectorAll(
      `.attr-input[data-category="${category}"]`,
    );
    let spent = 0;

    categoryInputs.forEach((inp) => (spent += parseInt(inp.value) - 1));

    if (spent > max) {
      categoryInputs.forEach((inp) => {
        inp.value = 1;
        inp.dataset.prev = 1;
      });
      document.getElementById(category + "-spent").innerText = 0;
    } else {
      document.getElementById(category + "-spent").innerText = spent;
    }
  }

  prioritySelects.forEach((select) => {
    select.addEventListener("change", updatePriorities);
  });

  attrInputs.forEach((input) => {
    input.dataset.prev = input.value;

    input.addEventListener("input", function () {
      let category = this.dataset.category;
      let max = parseInt(document.getElementById(category + "-max").innerText) || 0;
      let categoryInputs = document.querySelectorAll(
        `.attr-input[data-category="${category}"]`,
      );
      let spent = 0;

      categoryInputs.forEach((inp) => (spent += parseInt(inp.value) - 1));

      if (spent > max) {
        this.value = this.dataset.prev;
      } else {
        this.dataset.prev = this.value;
        document.getElementById(category + "-spent").innerText = spent;
      }
    });
  });

  // --- ABILITY LOGIC AND LIMITS ---
  const casteSelect = document.getElementById("caste-select");
  const abilityInputs = document.querySelectorAll(".ability-input");
  const abilitySpentDisplay = document.getElementById("ability-spent");
  const MAX_ABILITY_POINTS = 20;

  const casteAbilities = {
    Dawn: ["archery", "brawl", "martial-arts", "melee", "thrown"],
    Zenith: ["endurance", "performance", "presence", "resistance", "survival"],
    Twilight: ["craft", "investigation", "lore", "medicine", "occult"],
    Night: ["athletics", "awareness", "dodge", "larceny", "stealth"],
    Eclipse: ["bureaucracy", "linguistics", "ride", "sail", "socialize"],
  };

  function resetAbilities() {
    abilityInputs.forEach((input) => {
      input.value = 0;
      input.dataset.base = 0;
      input.dataset.prev = 0;
    });
  }

  function calculateAbilityPoints() {
    let spent = 0;
    abilityInputs.forEach((input) => {
      let val = parseInt(input.value) || 0;
      let base = parseInt(input.dataset.base) || 0;
      spent += val - base;
    });
    abilitySpentDisplay.innerText = spent;
    return spent;
  }

  function updateCasteBonus() {
    resetAbilities();
    const selectedCaste = casteSelect.value;

    if (casteAbilities[selectedCaste]) {
      casteAbilities[selectedCaste].forEach((ability) => {
        const input = document.getElementById("stat-" + ability);
        if (input) {
          input.value = 1;
          input.dataset.base = 1;
          input.dataset.prev = 1;
        }
      });
    }
    calculateAbilityPoints();
  }

  casteSelect.addEventListener("change", updateCasteBonus);

  abilityInputs.forEach((input) => {
    input.addEventListener("input", function () {
      let base = parseInt(this.dataset.base) || 0;

      // Prevent dropping below the base caste dot
      if (parseInt(this.value) < base) {
        this.value = base;
      }

      let spent = calculateAbilityPoints();

      // Prevent exceeding the max limit
      if (spent > MAX_ABILITY_POINTS) {
        this.value = this.dataset.prev;
        calculateAbilityPoints(); // Revert display
      } else {
        this.dataset.prev = this.value;
      }
    });
  });

  // Restore a saved sheet (or an invalid submission) after the caste defaults are applied.
  let initialData = {};
  const initialSheetNode = document.getElementById("initial-sheet-data");
  if (initialSheetNode) {
    try { initialData = JSON.parse(initialSheetNode.textContent || "{}"); }
    catch (error) { console.error("Could not parse initial character sheet", error); }
  }

  function setNamedValue(name, value) {
    const element = document.querySelector(`[name="${name}"]`);
    if (element && value !== undefined && value !== null) element.value = value;
  }

  // Initialize the caste baseline, then restore saved values without losing favored dots.
  if (initialData.caste) casteSelect.value = initialData.caste;
  prioritySelects.forEach((select) => {
    const category = select.dataset.category;
    if (initialData.priorities && initialData.priorities[category] !== undefined) {
      select.value = String(initialData.priorities[category]);
    }
  });
  updatePriorities();
  updateCasteBonus();

  ["name", "player_name", "concept", "nature", "anima", "personal-motes", "peripheral-motes", "backgrounds"].forEach((name) => {
    const keyMap = {"personal-motes": "personal_motes", "peripheral-motes": "peripheral_motes"};
    setNamedValue(name, initialData[keyMap[name] || name]);
  });

  attrInputs.forEach((input) => {
    const value = initialData.attributes && initialData.attributes[input.name];
    if (value !== undefined) input.value = value;
    input.dataset.prev = input.value;
  });
  updatePriorities();

  abilityInputs.forEach((input) => {
    const value = initialData.abilities && initialData.abilities[input.name];
    if (value !== undefined) input.value = Math.max(Number(input.dataset.base || 0), Number(value));
    input.dataset.prev = input.value;
    const specialty = initialData.specialties && initialData.specialties[input.name];
    if (specialty) {
      const specialtyInput = document.querySelector(`[name="${input.name}-specialty"]`);
      if (specialtyInput) specialtyInput.value = specialty;
    }
  });
  calculateAbilityPoints();

  (initialData.virtues ? Object.entries(initialData.virtues) : []).forEach(([name, value]) => setNamedValue(name, value));
  if (initialData.core) {
    setNamedValue("willpower", initialData.core.willpower);
    setNamedValue("essence", initialData.core.essence);
  }
  document.querySelectorAll("#virtues-advantages .stat-input").forEach((input) => { input.max = 5; });
  document.querySelectorAll("#core-traits .stat-input").forEach((input) => {
    if (input.name === "willpower") input.max = 10;
  });
});
