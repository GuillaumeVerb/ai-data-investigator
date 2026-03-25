const state = {
  lang: "fr",
  dataset: null,
  profile: null,
  investigation: null,
  training: null,
  copilot: null,
};

const copy = {
  fr: {
    heroCopy: "Un copilote d'analyse et de decision qui transforme un CSV en diagnostic, recommandations et actions.",
    controlsTitle: "Demarrer",
    controlsCopy: "Charge une demo ou importe un CSV pour lancer l'investigation.",
    salesDemo: "Charger la demo ventes",
    marketingDemo: "Charger la demo marketing",
    upload: "Importer un CSV",
    noData: "Aucune donnee chargee.",
    ready: "Pret pour la demo",
    emptyTitle: "Charge un dataset pour afficher la synthese decisionnelle.",
    emptyCopy: "L'interface affichera ensuite les insights, le signal principal, un chart cle et le copilote.",
    decisionKicker: "Decision Summary",
    decisionTitle: "Synthese decisionnelle",
    decisionSubtitle: "Les 5 messages a retenir pour comprendre quoi faire, pourquoi, et avec quel niveau de confiance.",
    snapshotKicker: "Business Snapshot",
    snapshotTitle: "Vue d'ensemble",
    previewSummary: "Apercu des donnees",
    insightsKicker: "What matters now",
    insightsTitle: "Top insights",
    chartKicker: "Key chart",
    chartTitle: "Signal principal",
    predictionKicker: "Prediction",
    predictionTitle: "Prediction engine",
    trainModel: "Entrainer le modele",
    copilotTitle: "Copilote",
    copilotAsk: "Interroger le copilote",
    copilotResultKicker: "Copilot answer",
    copilotResultTitle: "Reponse du copilote",
    questionPlaceholder: "Faut-il augmenter le prix ? Quel segment prioriser ?",
    connectError: "Impossible de joindre l'API.",
    loadingSales: "Chargement de la demo ventes...",
    loadingMarketing: "Chargement de la demo marketing...",
    loadingProfile: "Chargement du diagnostic...",
    uploadDone: "Dataset charge avec succes.",
    trainingDone: "Modele entraine avec succes.",
    askDone: "Reponse copilote mise a jour.",
    recommendation: "Recommandation",
    risk: "Risque principal",
    confidence: "Confiance",
    robustness: "Robustesse",
    nextStep: "Prochaine action",
    rows: "Lignes",
    columns: "Colonnes",
    coverage: "Couverture",
    quality: "Qualite",
    targetToModel: "Cible a modeliser",
    topDrivers: "Leviers principaux",
    metric: "Metrique cle",
    impact: "Impact",
    why: "Pourquoi c'est important",
    investigate: "Investiguer",
    noAnswer: "Pose une question pour voir la reponse du copilote.",
    noTraining: "Entraine un modele pour afficher les signaux predictifs.",
  },
  en: {
    heroCopy: "An AI decision copilot that turns a CSV into diagnosis, recommendations, and next actions.",
    controlsTitle: "Get started",
    controlsCopy: "Load a demo or upload a CSV to launch the investigation.",
    salesDemo: "Load sales demo",
    marketingDemo: "Load marketing demo",
    upload: "Upload a CSV",
    noData: "No dataset loaded yet.",
    ready: "Ready for demo",
    emptyTitle: "Load a dataset to unlock the decision summary.",
    emptyCopy: "The interface will then show the main insights, a key chart, prediction signals, and the copilot.",
    decisionKicker: "Decision Summary",
    decisionTitle: "Decision summary",
    decisionSubtitle: "The 5 messages that explain what to do, why it matters, and how confident the system is.",
    snapshotKicker: "Business Snapshot",
    snapshotTitle: "Overview",
    previewSummary: "Data preview",
    insightsKicker: "What matters now",
    insightsTitle: "Top insights",
    chartKicker: "Key chart",
    chartTitle: "Main signal",
    predictionKicker: "Prediction",
    predictionTitle: "Prediction engine",
    trainModel: "Train model",
    copilotTitle: "Copilot",
    copilotAsk: "Ask the copilot",
    copilotResultKicker: "Copilot answer",
    copilotResultTitle: "Copilot answer",
    questionPlaceholder: "Should we increase price? Which segment should we prioritize?",
    connectError: "Unable to reach the API.",
    loadingSales: "Loading sales demo...",
    loadingMarketing: "Loading marketing demo...",
    loadingProfile: "Loading investigation context...",
    uploadDone: "Dataset loaded successfully.",
    trainingDone: "Model trained successfully.",
    askDone: "Copilot answer updated.",
    recommendation: "Recommendation",
    risk: "Main risk",
    confidence: "Confidence",
    robustness: "Robustness",
    nextStep: "Next best step",
    rows: "Rows",
    columns: "Columns",
    coverage: "Coverage",
    quality: "Quality",
    targetToModel: "Target to model",
    topDrivers: "Top drivers",
    metric: "Primary metric",
    impact: "Impact",
    why: "Why it matters",
    investigate: "Investigate",
    noAnswer: "Ask a question to display the copilot answer.",
    noTraining: "Train a model to display predictive signals.",
  },
};

const $ = (id) => document.getElementById(id);

function currentCopy() {
  return copy[state.lang];
}

function setStatus(message, isError = false) {
  const node = $("status");
  node.textContent = message;
  node.classList.toggle("error", isError);
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function hydrateDataset(dataset) {
  state.dataset = dataset;
  setStatus(currentCopy().loadingProfile);
  const [profile, investigation] = await Promise.all([
    api("/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dataset_id: dataset.dataset_id, language: state.lang }),
    }),
    api("/investigate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dataset_id: dataset.dataset_id, language: state.lang }),
    }),
  ]);
  state.profile = profile;
  state.investigation = investigation;
  state.training = null;
  state.copilot = null;
  setStatus(`${currentCopy().uploadDone} ${dataset.filename}`);
  render();
}

function renderStaticCopy() {
  const c = currentCopy();
  document.documentElement.lang = state.lang;
  $("hero-copy").textContent = c.heroCopy;
  $("controls-title").textContent = c.controlsTitle;
  $("controls-copy").textContent = c.controlsCopy;
  $("load-sales").textContent = c.salesDemo;
  $("load-marketing").textContent = c.marketingDemo;
  $("upload-label").textContent = c.upload;
  $("empty-eyebrow").textContent = c.ready;
  $("empty-title").textContent = c.emptyTitle;
  $("empty-copy").textContent = c.emptyCopy;
  $("decision-kicker").textContent = c.decisionKicker;
  $("decision-title").textContent = c.decisionTitle;
  $("decision-subtitle").textContent = c.decisionSubtitle;
  $("snapshot-kicker").textContent = c.snapshotKicker;
  $("snapshot-title").textContent = c.snapshotTitle;
  $("preview-summary").textContent = c.previewSummary;
  $("insights-kicker").textContent = c.insightsKicker;
  $("insights-title").textContent = c.insightsTitle;
  $("chart-kicker").textContent = c.chartKicker;
  $("chart-title").textContent = c.chartTitle;
  $("prediction-kicker").textContent = c.predictionKicker;
  $("prediction-title").textContent = c.predictionTitle;
  $("train-model").textContent = c.trainModel;
  $("copilot-title").textContent = c.copilotTitle;
  $("ask-copilot").textContent = c.copilotAsk;
  $("copilot-result-kicker").textContent = c.copilotResultKicker;
  $("copilot-result-title").textContent = c.copilotResultTitle;
  $("question-input").placeholder = c.questionPlaceholder;
  $("lang-fr").classList.toggle("active", state.lang === "fr");
  $("lang-en").classList.toggle("active", state.lang === "en");
  if (!state.dataset) {
    setStatus(c.noData);
  }
}

function renderDecisionCards() {
  const c = currentCopy();
  const insight = state.investigation?.insights?.[0];
  const suggestion = state.investigation?.investigation_suggestions?.[0];
  const training = state.training;
  const cards = [
    { label: c.recommendation, value: state.investigation?.executive_brief || "-" },
    { label: c.risk, value: state.investigation?.anomaly_narrative || "-" },
    { label: c.confidence, value: training?.confidence_level || `${insight?.confidence_pct || 0}%` },
    { label: c.robustness, value: `${state.profile?.quality_score || "-"} / 100` },
    { label: c.nextStep, value: suggestion?.title || "-" },
  ];
  $("decision-cards").innerHTML = cards
    .map(
      (card) => `
        <article class="decision-card">
          <div class="decision-label">${card.label}</div>
          <div class="decision-value">${card.value}</div>
        </article>
      `,
    )
    .join("");
}

function renderDatasetMetrics() {
  const c = currentCopy();
  const metrics = [
    { label: c.rows, value: state.dataset.rows },
    { label: c.columns, value: state.dataset.columns },
    { label: c.coverage, value: `${state.profile.data_coverage_pct}%` },
    { label: c.quality, value: `${state.profile.quality_score}` },
  ];
  $("dataset-metrics").innerHTML = metrics
    .map(
      (metric) => `
        <article class="metric-card">
          <div class="small-meta">${metric.label}</div>
          <div class="metric-value">${metric.value}</div>
        </article>
      `,
    )
    .join("");

  const preview = state.dataset.preview || [];
  if (!preview.length) {
    $("preview-table").innerHTML = "";
    return;
  }
  const columns = Object.keys(preview[0]);
  const head = `<tr>${columns.map((col) => `<th>${col}</th>`).join("")}</tr>`;
  const rows = preview
    .slice(0, 8)
    .map((row) => `<tr>${columns.map((col) => `<td>${row[col] ?? ""}</td>`).join("")}</tr>`)
    .join("");
  $("preview-table").innerHTML = `<thead>${head}</thead><tbody>${rows}</tbody>`;
}

function renderInsights() {
  $("insights-grid").innerHTML = (state.investigation.insights || [])
    .slice(0, 3)
    .map(
      (item) => `
        <article class="insight-card">
          <span class="tag ${item.impact_level}">${item.impact_level}</span>
          <strong>${item.title}</strong>
          <p>${item.description}</p>
        </article>
      `,
    )
    .join("");
}

function renderChart() {
  const c = currentCopy();
  const chartSpec = state.investigation?.chart_specs?.[0];
  if (!chartSpec) {
    $("chart-story").innerHTML = "";
    $("chart-host").innerHTML = "";
    return;
  }
  $("chart-story").innerHTML = `
    <strong>${c.why}:</strong> ${chartSpec.why_it_matters || "-"}<br />
    <strong>${c.impact}:</strong> ${chartSpec.impact_level || "-"}<br />
    <strong>Insight:</strong> ${chartSpec.insight || "-"}
  `;
  Plotly.newPlot("chart-host", chartSpec.figure.data || chartSpec.figure, chartSpec.figure.layout || {}, {
    responsive: true,
    displayModeBar: false,
  });
}

function renderTargetOptions() {
  const select = $("target-select");
  const c = currentCopy();
  const options = state.profile?.target_candidates?.length ? state.profile.target_candidates : ["revenue"];
  select.innerHTML = options.map((option) => `<option value="${option}">${c.targetToModel}: ${option}</option>`).join("");
}

function renderTraining() {
  const c = currentCopy();
  if (!state.training) {
    $("training-summary").innerHTML = `<div class="answer-card">${c.noTraining}</div>`;
    return;
  }
  $("training-summary").innerHTML = `
    <article class="answer-card">
      <strong>${c.metric}</strong>
      <p>${state.training.primary_metric_name}: ${state.training.primary_metric_value}</p>
      <p>${c.confidence}: ${state.training.confidence_level}</p>
      <p>${c.coverage}: ${state.training.data_coverage_pct}%</p>
    </article>
    <article class="answer-card">
      <strong>${c.topDrivers}</strong>
      <p>${(state.training.top_drivers || []).join("<br />")}</p>
    </article>
  `;
}

function renderCopilot() {
  const c = currentCopy();
  if (!state.copilot) {
    $("copilot-answer").innerHTML = `<div class="answer-card">${c.noAnswer}</div>`;
    return;
  }
  $("copilot-answer").innerHTML = `
    <article class="answer-card">
      <strong>${state.copilot.short_answer || state.copilot.answer}</strong>
      <p>${state.copilot.answer}</p>
      <p><strong>${c.confidence}:</strong> ${state.copilot.confidence_level} (${state.copilot.confidence_score}/100)</p>
      <p><strong>${c.nextStep}:</strong><br />${(state.copilot.suggested_next_investigation || []).join("<br />")}</p>
    </article>
  `;
}

function render() {
  renderStaticCopy();
  const hasData = Boolean(state.dataset && state.profile && state.investigation);
  $("empty-state").hidden = hasData;
  $("dashboard").hidden = !hasData;
  if (!hasData) {
    return;
  }
  renderDecisionCards();
  renderDatasetMetrics();
  renderInsights();
  renderChart();
  renderTargetOptions();
  renderTraining();
  renderCopilot();
}

async function loadSample(name) {
  try {
    setStatus(name === "sales" ? currentCopy().loadingSales : currentCopy().loadingMarketing);
    const dataset = await api(`/upload/sample/${name}`, { method: "POST" });
    await hydrateDataset(dataset);
  } catch (error) {
    setStatus(`${currentCopy().connectError} ${error.message}`, true);
  }
}

async function uploadFile(file) {
  try {
    const form = new FormData();
    form.append("file", file);
    const dataset = await api("/upload", { method: "POST", body: form });
    await hydrateDataset(dataset);
  } catch (error) {
    setStatus(`${currentCopy().connectError} ${error.message}`, true);
  }
}

async function trainModel() {
  if (!state.dataset) return;
  try {
    const target = $("target-select").value;
    const training = await api("/train", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dataset_id: state.dataset.dataset_id, target }),
    });
    state.training = training;
    setStatus(currentCopy().trainingDone);
    render();
  } catch (error) {
    setStatus(`${currentCopy().connectError} ${error.message}`, true);
  }
}

async function askCopilot() {
  if (!state.dataset) return;
  const question = $("question-input").value.trim();
  if (!question) return;
  try {
    const payload = {
      dataset_id: state.dataset.dataset_id,
      question,
      target: $("target-select").value || null,
      language: state.lang,
    };
    state.copilot = await api("/copilot/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    setStatus(currentCopy().askDone);
    render();
  } catch (error) {
    setStatus(`${currentCopy().connectError} ${error.message}`, true);
  }
}

function bindEvents() {
  $("load-sales").addEventListener("click", () => loadSample("sales"));
  $("load-marketing").addEventListener("click", () => loadSample("marketing"));
  $("file-input").addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (file) uploadFile(file);
  });
  $("train-model").addEventListener("click", trainModel);
  $("ask-copilot").addEventListener("click", askCopilot);
  $("lang-fr").addEventListener("click", () => {
    state.lang = "fr";
    render();
  });
  $("lang-en").addEventListener("click", () => {
    state.lang = "en";
    render();
  });
}

bindEvents();
render();
