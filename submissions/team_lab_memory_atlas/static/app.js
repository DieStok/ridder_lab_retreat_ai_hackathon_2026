const state = window.ATLAS_STATE || { people: [], projects: [] };

const peopleGrid = document.querySelector("#people-grid");
const searchInput = document.querySelector("#atlas-search");
const clearButton = document.querySelector("#clear-filter");
const projectButtons = Array.from(document.querySelectorAll(".project-node"));
let activeProject = "";

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderList(items, emptyText) {
  const values = Array.isArray(items) && items.length ? items : [emptyText];
  return `<ul class="clean-list">${values.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function renderChips(items) {
  if (!Array.isArray(items) || !items.length) return "";
  return `<div class="chip-row">${items.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}</div>`;
}

function selectPerson(personId) {
  const person = state.people.find((item) => item.id === personId) || state.people[0];
  if (!person) return;

  document.querySelectorAll(".person-card").forEach((card) => {
    card.classList.toggle("active", card.dataset.personId === person.id);
  });

  document.querySelector("#inspector-name").textContent = person.name;
  document.querySelector("#inspector-role").textContent = person.role;
  const body = document.querySelector("#inspector-body");
  body.innerHTML = `
    <p>${escapeHtml(person.intro)}</p>
    ${person.is_global_supervisor ? '<div class="profile-meta-row"><span class="type-pill">PI / global supervisor</span></div>' : ""}
    ${renderChips(person.project_labels)}
    <div class="inspector-section">
      <h3>Supervision</h3>
      ${renderList([...(person.pi_supervisors || []).map((name) => `PI supervisor: ${name}`), ...(person.supervisors || []).map((name) => `Supervisor: ${name}`), ...(person.supervisees || []).map((name) => `Supervises: ${name}`)], "No supervisor links assigned yet.")}
    </div>
    <div class="inspector-section">
      <h3>Current topics</h3>
      ${renderList(person.topics, "No topics approved yet.")}
    </div>
    <div class="inspector-section">
      <h3>Recent updates</h3>
      ${renderList(person.recent_updates, "No meeting-approved updates yet.")}
    </div>
    <div class="inspector-section">
      <h3>Open challenges</h3>
      ${renderList(person.challenges, "No approved challenges yet.")}
    </div>
    <div class="inspector-section">
      <h3>Suggested helpers</h3>
      ${renderList(person.helpers, "No strong overlap yet.")}
    </div>
    <div class="inspector-section">
      <a class="primary-link" href="/people/${encodeURIComponent(person.id)}">Open profile</a>
    </div>
  `;
}

function filterPeople() {
  const query = (searchInput?.value || "").toLowerCase().trim();
  const cards = Array.from(document.querySelectorAll(".person-card"));
  let firstVisible = "";
  cards.forEach((card) => {
    const textMatch = !query || card.dataset.search.includes(query);
    const projectMatch = !activeProject || card.dataset.projects.split(" ").includes(activeProject);
    const visible = textMatch && projectMatch;
    card.classList.toggle("hidden", !visible);
    if (visible && !firstVisible) firstVisible = card.dataset.personId;
  });
  if (firstVisible) selectPerson(firstVisible);
}

if (peopleGrid) {
  peopleGrid.addEventListener("click", (event) => {
    const card = event.target.closest(".person-card");
    if (card) selectPerson(card.dataset.personId);
  });
  peopleGrid.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const card = event.target.closest(".person-card");
    if (card) {
      event.preventDefault();
      selectPerson(card.dataset.personId);
    }
  });
}

if (searchInput) searchInput.addEventListener("input", filterPeople);

if (clearButton) {
  clearButton.addEventListener("click", () => {
    if (searchInput) searchInput.value = "";
    activeProject = "";
    projectButtons.forEach((button) => button.classList.remove("active"));
    filterPeople();
  });
}

projectButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const nextProject = button.dataset.project;
    activeProject = activeProject === nextProject ? "" : nextProject;
    projectButtons.forEach((item) => item.classList.toggle("active", item.dataset.project === activeProject));
    filterPeople();
  });
});

if (state.people.length) selectPerson(state.people[0].id);
