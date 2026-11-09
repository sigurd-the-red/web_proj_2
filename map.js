/* Interactive location map, retaining the coordinates and descriptions from the supplied map.js. */
(() => {
  const mapElement = document.getElementById("map");
  if (!mapElement || typeof L === "undefined") return;

  const map = L.map("map", {
    crs: L.CRS.Simple,
    minZoom: -2,
    maxZoom: 2,
    zoomControl: true,
    attributionControl: false,
  });

  const imageWidth = 2000;
  const imageHeight = 1500;
  const bounds = [[0, 0], [imageHeight, imageWidth]];
  L.imageOverlay(mapElement.dataset.mapImage, bounds).addTo(map);
  map.fitBounds(bounds);
  map.setMaxBounds(bounds);

  const locations = [
    { name: "The Imperial City", coords: [762, 1082], description: "The heart of the Realm and seat of the missing Scarlet Empress." },
    { name: "Gem", coords: [240, 761], description: "The wealthy Southern metropolis. Wealth, splendor, and death await those who dare make the journey there." },
    { name: "The Lap", coords: [472, 875], description: "The dullest, most boring city in the world. Nothing ever happens here. So don't you dare visit..." },
    { name: "Paragon", coords: [474, 976], description: "Ruled by an undying mortal sorcerer, this colorless city is a place of peace and quiet. As long as one obeys its eternal master." },
    { name: "Chiaroscuro", coords: [490, 1019], description: "An abandoned city built entirely of glass, filled with relics of a greater age. Few dare travel here." },
    { name: "Nexus", coords: [773, 1305], description: "A great city with a singular law: everything goes, as long as there is profit to be made." },
    { name: "Lookshy", coords: [767, 1239], description: "The center of Dragonblooded power in these shattered lands. Endless is their work." },
  ];

  locations.forEach((location) => {
    const popup = document.createElement("div");
    const heading = document.createElement("h5");
    const paragraph = document.createElement("p");
    heading.textContent = location.name;
    paragraph.textContent = location.description;
    popup.append(heading, paragraph);
    L.marker(location.coords).addTo(map).bindPopup(popup);
  });

  map.on("click", (event) => {
    console.debug(`Map coordinates — Y: ${Math.round(event.latlng.lat)}, X: ${Math.round(event.latlng.lng)}`);
  });
})();
