const state = {
  lang: "fr",
  dataset: null,
  profile: null,
  investigation: null,
  training: null,
  simulation: null,
  decisionMeta: null,
  decisionResult: null,
  copilot: null,
  focusedAnalysis: null,
  health: null,
};

const copy = {
  fr: {
    heroCopy: "Un copilote d'analyse et de decision qui transforme un CSV en diagnostic, recommandations et actions.",
    controlsTitle: "Demarrer",
    controlsCopy: "Charge une demo ou importe un CSV pour lancer l'investigation.",
    workflowLoad: "Charger les donnees",
    workflowInsights: "Lire les insights",
    workflowTrain: "Entrainer le modele",
    workflowSimulate: "Simuler",
    workflowDecide: "Decider",
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
    simulationKicker: "Scenario simulation",
    simulationTitle: "Simulation guidee",
    runGuidedSimulation: "Lancer le scenario guide",
    simulationReady: "Simulation disponible",
    simulationBefore: "Avant",
    simulationAfter: "Apres",
    simulationDelta: "Delta",
    simulationDeltaPct: "Delta %",
    engineKicker: "Decision engine",
    engineTitle: "Moteur de decision",
    engineCopy: "Compare deux scenarios, visualise le risque et fais remonter la meilleure action.",
    baselineModeReference: "Ligne de reference",
    baselineModeAverage: "Moyenne dataset",
    referenceIndex: "Index de reference",
    prepareEngine: "Preparer les controles",
    runEngine: "Lancer le moteur de decision",
    scenarioA: "Scenario A",
    scenarioB: "Scenario B",
    unavailableInputs: "Entrees indisponibles",
    decisionReady: "Comparaison de scenarios disponible",
    noSimulation: "Lance une simulation guidee pour afficher un avant/apres sur la ligne de reference.",
    noDecisionBuilder: "Entraine un modele puis prepare le moteur de decision pour comparer deux scenarios.",
    noDecisionResult: "Le moteur de decision affichera ici la recommandation, le risque et les graphiques compares.",
    copilotTitle: "Copilote",
    copilotAsk: "Interroger le copilote",
    analysisTitle: "Signal du moment",
    focusedAnalysisEmpty: "Choisis une piste d'investigation pour afficher l'analyse detaillee.",
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
    suggestionsKicker: "Investigation suggestions",
    suggestionsTitle: "Ou investiguer ensuite",
    actionsKicker: "Recommended actions",
    actionsTitle: "Actions recommandees",
    evidenceKicker: "Evidence pack",
    evidenceTitle: "Pack de preuves",
    evidenceSummary: "Afficher les signaux utilises",
    evidenceMetrics: "Metriques cles",
    evidenceTargets: "Cibles detectees",
    evidenceDerived: "Signaux crees",
    evidenceQuality: "Qualite et couverture",
    confidenceKicker: "Confidence",
    confidenceTitle: "Confiance et limites",
    confidenceScore: "Score de confiance",
    confidenceWhy: "Pourquoi on y croit",
    confidenceLimit: "Limite principale",
    confidenceNext: "Ce qui renforcerait la reco",
    systemLabel: "Systeme",
    systemReady: "API operationnelle",
    llmLabel: "LLM",
    llmReady: "OpenAI connecte",
    modeLabel: "Mode",
    modeValue: "Decision-first workflow",
    noAnswer: "Pose une question pour voir la reponse du copilote.",
    noTraining: "Entraine un modele pour afficher les signaux predictifs.",
    exportTitle: "Rapport executif",
    exportCopy: "Exporte une synthese HTML a partager en revue client ou management.",
    exportReport: "Exporter le rapport",
    exportReady: "Rapport exporte",
  },
  en: {
    heroCopy: "An AI decision copilot that turns a CSV into diagnosis, recommendations, and next actions.",
    controlsTitle: "Get started",
    controlsCopy: "Load a demo or upload a CSV to launch the investigation.",
    workflowLoad: "Load data",
    workflowInsights: "Review insights",
    workflowTrain: "Train model",
    workflowSimulate: "Simulate",
    workflowDecide: "Decide",
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
    simulationKicker: "Scenario simulation",
    simulationTitle: "Guided simulation",
    runGuidedSimulation: "Run guided scenario",
    simulationReady: "Simulation ready",
    simulationBefore: "Before",
    simulationAfter: "After",
    simulationDelta: "Delta",
    simulationDeltaPct: "Delta %",
    engineKicker: "Decision engine",
    engineTitle: "Decision engine",
    engineCopy: "Compare two scenarios, surface the risk, and highlight the most robust action.",
    baselineModeReference: "Reference row",
    baselineModeAverage: "Dataset average",
    referenceIndex: "Reference index",
    prepareEngine: "Prepare controls",
    runEngine: "Run decision engine",
    scenarioA: "Scenario A",
    scenarioB: "Scenario B",
    unavailableInputs: "Unavailable inputs",
    decisionReady: "Scenario comparison ready",
    noSimulation: "Run a guided simulation to display a clear before/after effect on the reference row.",
    noDecisionBuilder: "Train a model, then prepare the decision engine to compare two scenarios.",
    noDecisionResult: "The decision engine will display the recommendation, key risk, and comparison charts here.",
    copilotTitle: "Copilot",
    copilotAsk: "Ask the copilot",
    analysisTitle: "Focus insight",
    focusedAnalysisEmpty: "Choose an investigation path to display the focused analysis.",
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
    suggestionsKicker: "Investigation suggestions",
    suggestionsTitle: "Where to investigate next",
    actionsKicker: "Recommended actions",
    actionsTitle: "Recommended actions",
    evidenceKicker: "Evidence pack",
    evidenceTitle: "Evidence pack",
    evidenceSummary: "Show supporting signals",
    evidenceMetrics: "Key metrics",
    evidenceTargets: "Detected targets",
    evidenceDerived: "Created signals",
    evidenceQuality: "Quality and coverage",
    confidenceKicker: "Confidence",
    confidenceTitle: "Confidence and limitations",
    confidenceScore: "Confidence score",
    confidenceWhy: "Why this is credible",
    confidenceLimit: "Main limitation",
    confidenceNext: "What would strengthen it",
    systemLabel: "System",
    systemReady: "API ready",
    llmLabel: "LLM",
    llmReady: "OpenAI connected",
    modeLabel: "Mode",
    modeValue: "Decision-first workflow",
    noAnswer: "Ask a question to display the copilot answer.",
    noTraining: "Train a model to display predictive signals.",
    exportTitle: "Executive report",
    exportCopy: "Export an HTML summary you can share in a client or management review.",
    exportReport: "Export report",
    exportReady: "Report exported",
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
  state.simulation = null;
  state.decisionMeta = null;
  state.decisionResult = null;
  state.copilot = null;
  state.focusedAnalysis = null;
  setStatus(`${currentCopy().uploadDone} ${dataset.filename}`);
  render();
}

async function refreshHealth() {
  try {
    state.health = await api("/health");
  } catch (_error) {
    state.health = null;
  }
}

function getGuidedSimulationChanges(referenceRow) {
  const changes = {};
  if (!referenceRow) return changes;
  if (referenceRow.price !== undefined && referenceRow.price !== null) {
    changes.price = Number(referenceRow.price) * 1.08;
  }
  if (referenceRow.marketing_spend !== undefined && referenceRow.marketing_spend !== null) {
    changes.marketing_spend = Number(referenceRow.marketing_spend) * 1.05;
  }
  const discountKey = referenceRow.discount_pct !== undefined ? "discount_pct" : referenceRow.discount !== undefined ? "discount" : null;
  if (discountKey && referenceRow[discountKey] !== null) {
    changes.discount = Math.max(0, Number(referenceRow[discountKey]) - 1);
  }
  return changes;
}

function currentBaselineMode() {
  return $("baseline-mode-select")?.value || "reference_row";
}

function currentReferenceIndex() {
  const raw = $("reference-index-input")?.value;
  return currentBaselineMode() === "reference_row" ? Number(raw || 0) : null;
}

function readScenarioValues(scope) {
  const values = {};
  document.querySelectorAll(`[data-scope="${scope}"]`).forEach((input) => {
    const key = input.dataset.key;
    if (!key) return;
    values[key] = input.dataset.controlType === "slider" ? Number(input.value) : input.value;
  });
  return values;
}

function readSegmentControls() {
  return {
    segment_column: $("decision-segment-column")?.value || null,
    segment_value: $("decision-segment-value")?.value || null,
  };
}

function downloadHtml(filename, html) {
  const blob = new Blob([html], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function renderStaticCopy() {
  const c = currentCopy();
  const baselineMode = $("baseline-mode-select")?.value || "reference_row";
  const referenceIndex = $("reference-index-input")?.value || "0";
  document.documentElement.lang = state.lang;
  $("hero-copy").textContent = c.heroCopy;
  $("controls-title").textContent = c.controlsTitle;
  $("controls-copy").textContent = c.controlsCopy;
  $("export-title").textContent = c.exportTitle;
  $("export-copy").textContent = c.exportCopy;
  $("export-report").textContent = c.exportReport;
  $("load-sales").textContent = c.salesDemo;
  $("load-marketing").textContent = c.marketingDemo;
  $("upload-label").textContent = c.upload;
  $("empty-eyebrow").textContent = c.ready;
  $("empty-title").textContent = c.emptyTitle;
  $("empty-copy").textContent = c.emptyCopy;
  $("decision-kicker").textContent = c.decisionKicker;
  $("decision-title").textContent = c.decisionTitle;
  $("decision-subtitle").textContent = c.decisionSubtitle;
  $("confidence-kicker").textContent = c.confidenceKicker;
  $("confidence-title").textContent = c.confidenceTitle;
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
  $("simulation-kicker").textContent = c.simulationKicker;
  $("simulation-title").textContent = c.simulationTitle;
  $("run-guided-simulation").textContent = c.runGuidedSimulation;
  $("engine-kicker").textContent = c.engineKicker;
  $("engine-title").textContent = c.engineTitle;
  $("engine-copy").textContent = c.engineCopy;
  $("prepare-decision-engine").textContent = c.prepareEngine;
  $("run-decision-engine").textContent = c.runEngine;
  $("copilot-title").textContent = c.copilotTitle;
  $("analysis-title").textContent = c.analysisTitle;
  $("focused-analysis-empty").textContent = c.focusedAnalysisEmpty;
  $("ask-copilot").textContent = c.copilotAsk;
  $("copilot-result-kicker").textContent = c.copilotResultKicker;
  $("copilot-result-title").textContent = c.copilotResultTitle;
  $("suggestions-kicker").textContent = c.suggestionsKicker;
  $("suggestions-title").textContent = c.suggestionsTitle;
  $("actions-kicker").textContent = c.actionsKicker;
  $("actions-title").textContent = c.actionsTitle;
  $("evidence-kicker").textContent = c.evidenceKicker;
  $("evidence-title").textContent = c.evidenceTitle;
  $("evidence-summary").textContent = c.evidenceSummary;
  $("baseline-mode-select").innerHTML = `
    <option value="reference_row">${c.baselineModeReference}</option>
    <option value="dataset_average">${c.baselineModeAverage}</option>
  `;
  $("baseline-mode-select").value = baselineMode;
  $("reference-index-input").placeholder = c.referenceIndex;
  $("reference-index-input").value = referenceIndex;
  $("question-input").placeholder = c.questionPlaceholder;
  $("band-status-label").textContent = c.systemLabel;
  $("band-status-value").textContent = state.health?.status === "ok" ? c.systemReady : c.connectError;
  $("band-llm-label").textContent = c.llmLabel;
  $("band-llm-value").textContent = state.health?.llm_enabled === "true" ? `${state.health.llm_provider} (${state.health.llm_model})` : "fallback";
  $("band-mode-label").textContent = c.modeLabel;
  $("band-mode-value").textContent = c.modeValue;
  $("lang-fr").classList.toggle("active", state.lang === "fr");
  $("lang-en").classList.toggle("active", state.lang === "en");
  if (!state.dataset) {
    setStatus(c.noData);
  }
}

function renderWorkflow() {
  const c = currentCopy();
  const steps = [
    { key: "load", label: c.workflowLoad, complete: Boolean(state.dataset), active: !state.dataset },
    { key: "insights", label: c.workflowInsights, complete: Boolean(state.investigation), active: Boolean(state.dataset && !state.training) },
    { key: "train", label: c.workflowTrain, complete: Boolean(state.training), active: Boolean(state.dataset && !state.training) },
    { key: "simulate", label: c.workflowSimulate, complete: Boolean(state.simulation), active: Boolean(state.training && !state.simulation) },
    { key: "decide", label: c.workflowDecide, complete: Boolean(state.decisionResult), active: Boolean(state.simulation && !state.decisionResult) },
  ];
  $("workflow-steps").innerHTML = steps
    .map(
      (step, index) => `
        <article class="workflow-step ${step.complete ? "complete" : ""} ${step.active ? "active" : ""}">
          <div class="workflow-step-number">${index + 1}</div>
          <div class="small-meta">${step.label}</div>
        </article>
      `,
    )
    .join("");
}

function renderDecisionCards() {
  const c = currentCopy();
  const insight = state.investigation?.insights?.[0];
  const suggestion = state.investigation?.investigation_suggestions?.[0];
  const training = state.training;
  const cards = [
    { icon: "🎯", label: c.recommendation, value: state.investigation?.executive_brief || "-" },
    { icon: "⚠️", label: c.risk, value: state.investigation?.anomaly_narrative || "-" },
    { icon: "📊", label: c.confidence, value: training?.confidence_level || `${insight?.confidence_pct || 0}%` },
    { icon: "🧠", label: c.robustness, value: `${state.profile?.quality_score || "-"} / 100` },
    { icon: "➡️", label: c.nextStep, value: suggestion?.title || "-" },
  ];
  $("decision-cards").innerHTML = cards
    .map(
      (card) => `
        <article class="decision-card">
          <div class="decision-icon">${card.icon}</div>
          <div class="decision-label">${card.label}</div>
          <div class="decision-value">${card.value}</div>
        </article>
      `,
    )
    .join("");
}

function renderConfidence() {
  const c = currentCopy();
  const confidenceLevel = state.decisionResult?.confidence?.level || state.training?.confidence_level || "medium";
  const confidenceValue = state.decisionResult?.confidence?.row_coverage_pct || state.training?.data_coverage_pct || state.profile?.data_coverage_pct || "-";
  const mainLimit = state.decisionResult?.main_risk || state.investigation?.anomaly_narrative || "-";
  const support = state.decisionResult?.supporting_evidence?.[0] || state.profile?.headline_findings?.[0] || state.investigation?.executive_brief || "-";
  const nextStrength = state.decisionResult?.next_best_analysis || state.investigation?.investigation_suggestions?.[0]?.title || "-";
  $("confidence-grid").innerHTML = `
    <article class="confidence-card">
      <strong>${c.confidenceScore}</strong>
      <p>${confidenceLevel}</p>
      <div class="small-meta">${confidenceValue}%</div>
    </article>
    <article class="confidence-card">
      <strong>${c.confidenceWhy}</strong>
      <p>${support}</p>
    </article>
    <article class="confidence-card">
      <strong>${c.confidenceLimit}</strong>
      <p>${mainLimit}</p>
    </article>
    <article class="confidence-card">
      <strong>${c.confidenceNext}</strong>
      <p>${nextStrength}</p>
    </article>
  `;
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
          <div class="small-meta">${item.confidence_pct}% confidence</div>
        </article>
      `,
    )
    .join("");
}

function renderChart() {
  const c = currentCopy();
  const chartSpec = state.investigation?.chart_specs?.[0];
  const secondaryChart = state.training?.feature_importance_chart
    ? {
        figure: state.training.feature_importance_chart,
        insight: (state.training.top_drivers || []).slice(0, 2).join(", "),
        why_it_matters: c.topDrivers,
        impact_level: state.training.confidence_level || "medium",
      }
    : state.investigation?.chart_specs?.[1];
  if (!chartSpec) {
    $("chart-story").innerHTML = "";
    $("chart-host").innerHTML = "";
    $("chart-story-secondary").innerHTML = "";
    $("chart-host-secondary").innerHTML = "";
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
  if (!secondaryChart) {
    $("chart-story-secondary").innerHTML = "";
    $("chart-host-secondary").innerHTML = "";
    return;
  }
  $("chart-story-secondary").innerHTML = `
    <strong>${c.why}:</strong> ${secondaryChart.why_it_matters || "-"}<br />
    <strong>${c.impact}:</strong> ${secondaryChart.impact_level || "-"}<br />
    <strong>Insight:</strong> ${secondaryChart.insight || "-"}
  `;
  Plotly.newPlot(
    "chart-host-secondary",
    secondaryChart.figure.data || secondaryChart.figure,
    secondaryChart.figure.layout || {},
    { responsive: true, displayModeBar: false },
  );
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

function renderSimulation() {
  const c = currentCopy();
  if (!state.training) {
    $("simulation-summary").innerHTML = `<div class="answer-card">${c.noSimulation}</div>`;
    $("simulation-status").textContent = "";
    return;
  }
  if (!state.simulation) {
    $("simulation-summary").innerHTML = `<div class="answer-card">${c.noSimulation}</div>`;
    $("simulation-status").textContent = "";
    return;
  }
  $("simulation-status").textContent = c.simulationReady;
  $("simulation-summary").innerHTML = `
    <div class="metric-grid">
      <article class="metric-card">
        <div class="small-meta">${c.simulationBefore}</div>
        <div class="metric-value">${state.simulation.prediction_before}</div>
      </article>
      <article class="metric-card">
        <div class="small-meta">${c.simulationAfter}</div>
        <div class="metric-value">${state.simulation.prediction_after}</div>
      </article>
      <article class="metric-card">
        <div class="small-meta">${c.simulationDelta}</div>
        <div class="metric-value">${state.simulation.delta}</div>
      </article>
      <article class="metric-card">
        <div class="small-meta">${c.simulationDeltaPct}</div>
        <div class="metric-value">${state.simulation.delta_pct ?? "-"}</div>
      </article>
    </div>
    <article class="answer-card">
      <strong>${state.simulation.impact_summary}</strong>
      <p>${state.simulation.narrative}</p>
      <p class="small-meta">${state.simulation.guardrail_note}</p>
    </article>
  `;
}

function renderDecisionBuilder() {
  const c = currentCopy();
  const host = $("decision-builder");
  if (!state.training || !state.decisionMeta) {
    host.innerHTML = `<div class="answer-card">${c.noDecisionBuilder}</div>`;
    return;
  }
  const availableInputs = (state.decisionMeta.available_inputs || []).filter((item) => item.available !== false);
  const unavailableInputs = (state.decisionMeta.available_inputs || []).filter((item) => item.available === false);
  const segmentColumnControl = availableInputs.find((item) => item.key === "segment_column");
  const segmentValueControl = availableInputs.find((item) => item.key === "segment_value");
  const scenarioControls = availableInputs.filter((item) => !["segment_column", "segment_value"].includes(item.key));

  const renderControl = (scope, control, prefix) => {
    if (control.control_type === "slider") {
      return `
        <div class="control-block">
          <label>${prefix} - ${control.label}</label>
          <input
            type="range"
            min="${control.min_value ?? 0}"
            max="${control.max_value ?? 100}"
            step="0.1"
            value="${control.default_value ?? 0}"
            data-scope="${scope}"
            data-key="${control.key}"
            data-control-type="slider"
          />
          <div class="small-meta">${control.default_value ?? 0}</div>
        </div>
      `;
    }
    return `
      <div class="control-block">
        <label>${prefix} - ${control.label}</label>
        <select data-scope="${scope}" data-key="${control.key}" data-control-type="selectbox">
          ${(control.options || [])
            .map((option) => `<option value="${option}" ${String(option) === String(control.default_value) ? "selected" : ""}>${option}</option>`)
            .join("")}
        </select>
      </div>
    `;
  };

  host.innerHTML = `
    ${
      segmentColumnControl || segmentValueControl
        ? `
      <div class="scenario-column">
        <strong>${c.impact}</strong>
        ${segmentColumnControl ? `
          <div class="control-block">
            <label>${segmentColumnControl.label}</label>
            <select id="decision-segment-column">
              ${(segmentColumnControl.options || [])
                .map((option) => `<option value="${option}" ${String(option) === String(segmentColumnControl.default_value) ? "selected" : ""}>${option}</option>`)
                .join("")}
            </select>
          </div>
        ` : ""}
        ${segmentValueControl ? `
          <div class="control-block">
            <label>${segmentValueControl.label}</label>
            <select id="decision-segment-value">
              ${(segmentValueControl.options || [])
                .map((option) => `<option value="${option}" ${String(option) === String(segmentValueControl.default_value) ? "selected" : ""}>${option}</option>`)
                .join("")}
            </select>
          </div>
        ` : ""}
      </div>
    `
        : ""
    }
    <div class="scenario-builder-grid">
      <div class="scenario-column">
        <strong>${c.scenarioA}</strong>
        ${scenarioControls.map((control) => renderControl("scenario_a", control, c.scenarioA)).join("")}
      </div>
      <div class="scenario-column">
        <strong>${c.scenarioB}</strong>
        ${scenarioControls.map((control) => renderControl("scenario_b", control, c.scenarioB)).join("")}
      </div>
    </div>
    ${
      unavailableInputs.length
        ? `
      <article class="answer-card">
        <strong>${c.unavailableInputs}</strong>
        <p>${unavailableInputs.map((item) => `${item.label}: ${item.reason || "-"}`).join("<br />")}</p>
      </article>
    `
        : ""
    }
  `;
}

function renderDecisionResult() {
  const c = currentCopy();
  const host = $("decision-result");
  if (!state.decisionResult) {
    host.innerHTML = `<div class="answer-card">${c.noDecisionResult}</div>`;
    return;
  }
  host.innerHTML = `
    <div class="decision-result-grid">
      <article class="answer-card">
        <strong>${c.recommendation}</strong>
        <p>${state.decisionResult.recommended_decision}</p>
      </article>
      <article class="answer-card">
        <strong>${c.risk}</strong>
        <p>${state.decisionResult.main_risk}</p>
      </article>
      <article class="answer-card">
        <strong>${c.confidence}</strong>
        <p>${state.decisionResult.confidence.level}</p>
      </article>
      <article class="answer-card">
        <strong>${c.nextStep}</strong>
        <p>${state.decisionResult.next_best_analysis}</p>
      </article>
    </div>
    <article class="answer-card">
      <strong>${c.actionsTitle}</strong>
      <p>${(state.decisionResult.supporting_evidence || []).join("<br />")}</p>
    </article>
    <div id="decision-result-charts" class="decision-chart-grid"></div>
  `;
  const chartHost = $("decision-result-charts");
  chartHost.innerHTML = "";
  (state.decisionResult.chart_specs || []).slice(0, 2).forEach((chart, index) => {
    const box = document.createElement("div");
    box.className = "decision-chart-box";
    box.innerHTML = `<strong>${chart.title || `Chart ${index + 1}`}</strong><div id="decision-chart-${index}" class="decision-chart-host"></div>`;
    chartHost.appendChild(box);
    Plotly.newPlot(`decision-chart-${index}`, chart.figure.data || chart.figure, chart.figure.layout || {}, {
      responsive: true,
      displayModeBar: false,
    });
  });
}

function renderActions() {
  $("actions-grid").innerHTML = (state.investigation?.recommended_actions || [])
    .slice(0, 3)
    .map(
      (item) => `
        <article class="insight-card">
          <span class="tag ${item.priority}">${item.priority}</span>
          <strong>${item.title}</strong>
          <p>${item.rationale}</p>
          <div class="small-meta">${item.expected_effect}</div>
        </article>
      `,
    )
    .join("");
}

function renderSuggestions() {
  const c = currentCopy();
  $("suggestions-grid").innerHTML = (state.investigation?.investigation_suggestions || [])
    .slice(0, 4)
    .map(
      (item) => `
        <article class="suggestion-card">
          <strong>${item.title}</strong>
          <p>${item.explanation}</p>
          <div class="pill-row">
            <span class="pill ${item.expected_impact.toLowerCase()}">${c.impact}: ${item.expected_impact}</span>
            <span class="pill">${c.confidence}: ${item.confidence_pct}%</span>
          </div>
          <div class="suggestion-footer">
            <div class="small-meta">${item.investigation_type}</div>
            <button class="secondary-btn investigate-btn" type="button" data-suggestion-id="${item.suggestion_id}">
              ${c.investigate}
            </button>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderFocusedAnalysis() {
  const c = currentCopy();
  if (!state.focusedAnalysis) {
    $("focused-analysis").innerHTML = `<div class="answer-card">${c.focusedAnalysisEmpty}</div>`;
    return;
  }
  $("focused-analysis").innerHTML = `
    <article class="answer-card">
      <strong>${state.focusedAnalysis.title}</strong>
      <p>${state.focusedAnalysis.analysis}</p>
      <p><strong>${c.impact}:</strong> ${state.focusedAnalysis.business_implication}</p>
    </article>
  `;
}

function renderEvidencePack() {
  const c = currentCopy();
  const cards = [
    {
      title: c.evidenceMetrics,
      body: `
        ${c.rows}: ${state.dataset.rows}<br />
        ${c.columns}: ${state.dataset.columns}<br />
        ${c.coverage}: ${state.profile.data_coverage_pct}%<br />
        ${c.quality}: ${state.profile.quality_score}
      `,
    },
    {
      title: c.evidenceTargets,
      body: (state.profile.target_candidates || []).join("<br />") || "-",
    },
    {
      title: c.evidenceDerived,
      body: (state.profile.derived_features || []).join("<br />") || "-",
    },
    {
      title: c.evidenceQuality,
      body: (state.profile.headline_findings || []).join("<br />"),
    },
  ];
  $("evidence-pack").innerHTML = cards
    .map(
      (card) => `
        <article class="evidence-card">
          <strong>${card.title}</strong>
          <p>${card.body}</p>
        </article>
      `,
    )
    .join("");
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
  renderWorkflow();
  const hasData = Boolean(state.dataset && state.profile && state.investigation);
  $("empty-state").hidden = hasData;
  $("dashboard").hidden = !hasData;
  if (!hasData) {
    return;
  }
  renderDecisionCards();
  renderConfidence();
  renderDatasetMetrics();
  renderInsights();
  renderSuggestions();
  renderChart();
  renderTargetOptions();
  renderTraining();
  renderSimulation();
  renderDecisionBuilder();
  renderDecisionResult();
  renderActions();
  renderFocusedAnalysis();
  renderEvidencePack();
  renderCopilot();
  bindDynamicEvents();
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
    state.simulation = null;
    state.decisionMeta = null;
    state.decisionResult = null;
    setStatus(currentCopy().trainingDone);
    await prepareDecisionEngine();
    render();
  } catch (error) {
    setStatus(`${currentCopy().connectError} ${error.message}`, true);
  }
}

async function runGuidedSimulation() {
  if (!state.dataset || !state.training) return;
  try {
    const changes = getGuidedSimulationChanges(state.training.reference_row);
    state.simulation = await api("/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        model_id: state.training.model_id,
        changes,
      }),
    });
    setStatus(currentCopy().simulationReady);
    renderSimulation();
  } catch (error) {
    setStatus(`${currentCopy().connectError} ${error.message}`, true);
  }
}

async function prepareDecisionEngine() {
  if (!state.dataset || !state.training) return;
  try {
    state.decisionMeta = await api("/decision-engine", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        model_id: state.training.model_id,
        baseline_mode: currentBaselineMode(),
        reference_index: currentReferenceIndex(),
        language: state.lang,
        scenario_a: {},
        scenario_b: {},
      }),
    });
    state.decisionResult = null;
    setStatus(currentCopy().decisionReady);
    renderDecisionBuilder();
    renderDecisionResult();
  } catch (error) {
    setStatus(`${currentCopy().connectError} ${error.message}`, true);
  }
}

async function runDecisionEngine() {
  if (!state.dataset || !state.training) return;
  try {
    const segmentControls = readSegmentControls();
    state.decisionResult = await api("/decision-engine", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        model_id: state.training.model_id,
        baseline_mode: currentBaselineMode(),
        reference_index: currentReferenceIndex(),
        segment_column: segmentControls.segment_column,
        segment_value: segmentControls.segment_value,
        language: state.lang,
        scenario_a: readScenarioValues("scenario_a"),
        scenario_b: readScenarioValues("scenario_b"),
      }),
    });
    setStatus(currentCopy().decisionReady);
    renderDecisionResult();
  } catch (error) {
    setStatus(`${currentCopy().connectError} ${error.message}`, true);
  }
}

async function investigateSuggestion(suggestionId) {
  if (!state.dataset || !state.investigation) return;
  const suggestion = (state.investigation.investigation_suggestions || []).find((item) => item.suggestion_id === suggestionId);
  if (!suggestion) return;
  try {
    state.focusedAnalysis = await api("/investigate-path", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        suggestion_id: suggestion.suggestion_id,
        payload: suggestion.payload,
        language: state.lang,
      }),
    });
    renderFocusedAnalysis();
    setStatus(suggestion.title);
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

async function exportReport() {
  const c = currentCopy();
  if (!state.dataset || !state.profile || !state.investigation) return;
  try {
    const payload = {
      dataset_id: state.dataset.dataset_id,
      profile: state.profile,
      investigation: state.investigation,
      training: state.training || null,
      simulation: state.simulation || null,
      root_cause: null,
    };
    const report = await api("/report/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    downloadHtml(`${report.title || "ai-data-investigator-report"}.html`, report.html_content);
    setStatus(c.exportReady);
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
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
  $("run-guided-simulation").addEventListener("click", runGuidedSimulation);
  $("prepare-decision-engine").addEventListener("click", prepareDecisionEngine);
  $("run-decision-engine").addEventListener("click", runDecisionEngine);
  $("ask-copilot").addEventListener("click", askCopilot);
  $("export-report").addEventListener("click", exportReport);
  $("lang-fr").addEventListener("click", () => {
    state.lang = "fr";
    if (state.dataset) {
      hydrateDataset(state.dataset);
    } else {
      render();
    }
  });
  $("lang-en").addEventListener("click", () => {
    state.lang = "en";
    if (state.dataset) {
      hydrateDataset(state.dataset);
    } else {
      render();
    }
  });
}

function bindDynamicEvents() {
  document.querySelectorAll(".investigate-btn").forEach((button) => {
    button.onclick = () => investigateSuggestion(button.dataset.suggestionId);
  });
  document.querySelectorAll('input[type="range"][data-control-type="slider"]').forEach((input) => {
    input.oninput = () => {
      const meta = input.nextElementSibling;
      if (meta) meta.textContent = input.value;
    };
  });
}

async function init() {
  await refreshHealth();
  bindEvents();
  render();
}

init();
