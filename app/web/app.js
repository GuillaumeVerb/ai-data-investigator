const state = {
  routePage: document.body.dataset.page || "decision",
  routePresetApplied: false,
  lang: "fr",
  dataset: null,
  profile: null,
  investigation: null,
  training: null,
  simulation: null,
  decisionMeta: null,
  decisionResult: null,
  copilot: null,
  sqlQuery: null,
  sqlHistory: [],
  focusedAnalysis: null,
  health: null,
  datasets: [],
  builderOps: {
    lastRoute: null,
    lastLatencyMs: null,
    queryCount: 0,
    usedTables: [],
  },
  joinAssistant: null,
  semanticLayer: null,
  prepAgent: null,
  workflowBuilder: null,
  quantOptimizer: null,
  observability: null,
  constraintSolver: null,
  experimentDesigner: null,
  evaluationConsole: null,
  policyEngine: null,
  semanticKpiRegistry: null,
  orchestrationView: null,
  platformOverview: null,
  latestConnectorTest: null,
  latestWorkflowExport: null,
  latestPolicyExport: null,
  latestApproval: null,
  marketProfile: "revenue",
  surfaceMode: "decision",
  surfaceSubtabs: {
    decision: "overview",
    builder: "sql",
    governance: "platform",
  },
};

const ROUTE_PATHS = {
  decision: "/decision",
  builder: "/builder",
  governance: "/gouvernance",
};

const ROUTE_DEFAULT_PROFILES = {
  decision: "revenue",
  builder: "builder",
  governance: "analytics",
};

const copy = {
  fr: {
    heroEyebrow: "Copilote de decision IA",
    heroCopy: "Un accelerateur de copilotes de decision pour transformer des donnees metier en diagnostics, simulations et recommandations defendables.",
    heroAudienceKicker: "Pour qui",
    heroAudienceTitle: "Revenue, pricing, croissance et consultants IA",
    heroAudienceCopy: "Pour les equipes qui doivent expliquer vite ce qui change, tester des scenarios et recommander une action claire.",
    heroValueKicker: "Ce que ca fait",
    heroValueTitle: "Investigue, simule et decide avec preuves",
    heroValueCopy: "Le produit combine analyse, SQL, scenarios, guardrails, evidence pack et exports dans un meme workflow.",
    heroModeKicker: "Deux modes",
    heroModeTitle: "Copilote de decision + Studio Builder IA",
    heroModeCopy: "Une couche simple pour decider, une couche avancee pour builder, gouverner et exporter des copilotes.",
    heroUsecase1: "Decision tarifaire",
    heroUsecase2: "Investigation revenue",
    heroUsecase3: "Optimisation de la croissance",
    heroUsecase4: "Workflows AI Builder",
    controlsTitle: "Lancer une analyse",
    controlsCopy: "Charge une demo revenue ou importe un CSV pour activer un copilote de decision complet.",
    workflowLoad: "Charger les donnees",
    workflowInsights: "Lire les insights",
    workflowTrain: "Entrainer le modele",
    workflowSimulate: "Simuler",
    workflowDecide: "Decider",
    salesDemo: "Charger la demo ventes",
    marketingDemo: "Charger la demo marketing",
    upload: "Importer un CSV",
    noData: "Aucune donnee chargee.",
    ready: "Pret pour une demo client",
    emptyTitle: "Charge un dataset pour activer le copilote de decision.",
    emptyCopy: "Tu verras ensuite les insights prioritaires, les scenarios, les recommandations et le studio AI Builder.",
    decisionKicker: "Synthese de decision",
    decisionTitle: "Synthese decisionnelle",
    decisionSubtitle: "Les 5 messages a retenir pour comprendre quoi faire, pourquoi, et avec quel niveau de confiance.",
    snapshotKicker: "Vue business",
    snapshotTitle: "Vue d'ensemble",
    previewSummary: "Apercu des donnees",
    insightsKicker: "Ce qui compte maintenant",
    insightsTitle: "Insights prioritaires",
    chartKicker: "Graphiques cles",
    chartTitle: "Signal principal",
    predictionKicker: "Prediction",
    predictionTitle: "Moteur predictif",
    trainModel: "Entrainer le modele",
    simulationKicker: "Simulation de scenario",
    simulationTitle: "Simulation guidee",
    runGuidedSimulation: "Lancer le scenario guide",
    simulationReady: "Simulation disponible",
    simulationBefore: "Avant",
    simulationAfter: "Apres",
    simulationDelta: "Delta",
    simulationDeltaPct: "Delta %",
    engineKicker: "Moteur de decision",
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
    copilotResultKicker: "Reponse du copilote",
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
    suggestionsKicker: "Pistes d investigation",
    suggestionsTitle: "Ou investiguer ensuite",
    actionsKicker: "Actions recommandees",
    actionsTitle: "Actions recommandees",
    evidenceKicker: "Pack de preuves",
    evidenceTitle: "Pack de preuves",
    evidenceSummary: "Afficher les signaux utilises",
    evidenceMetrics: "Metriques cles",
    evidenceTargets: "Cibles detectees",
    evidenceDerived: "Signaux crees",
    evidenceQuality: "Qualite et couverture",
    confidenceKicker: "Confiance",
    confidenceTitle: "Confiance et limites",
    confidenceScore: "Score de confiance",
    confidenceWhy: "Pourquoi on y croit",
    confidenceLimit: "Limite principale",
    confidenceNext: "Ce qui renforcerait la reco",
    systemLabel: "Systeme",
    systemReady: "API operationnelle",
    llmLabel: "LLM",
    llmReady: "OpenAI connecte",
    modeLabel: "Positionnement",
    modeValue: "Accelerateur de copilotes de decision",
    noAnswer: "Pose une question pour voir la reponse du copilote.",
    noTraining: "Entraine un modele pour afficher les signaux predictifs.",
    exportTitle: "Rapport executif",
    exportCopy: "Exporte une synthese HTML a partager en revue client ou management.",
    exportReport: "Exporter le rapport",
    exportReady: "Rapport exporte",
    queryTitle: "Interroger les donnees",
    queryPlaceholder: "Quel est le revenu moyen par region ?",
    queryRun: "Generer le SQL",
    queryRoute: "Router la question",
    queryRouterCopy: "Choisit automatiquement entre SQL, prediction, simulation ou copilote.",
    queryKicker: "Builder IA",
    queryResultTitle: "Question metier vers SQL",
    queryEmpty: "Pose une question sur les donnees pour afficher le SQL genere, le resultat et l'explication.",
    querySql: "SQL genere",
    queryRows: "Lignes retournees",
    queryWarning: "Avertissements",
    queryExplain: "Expliquer ce SQL",
    queryExplainDone: "Explication SQL mise a jour.",
    queryExport: "Exporter CSV",
    queryExportDone: "Resultat SQL exporte en CSV.",
    queryHistoryKicker: "Historique",
    queryHistoryTitle: "Historique des requetes",
    queryHistoryEmpty: "Les requetes SQL executees apparaitront ici.",
    queryHistoryReplay: "Relancer",
    routeSqlDone: "Question routee vers SQL.",
    routePredictionDone: "Question routee vers prediction.",
    routeSimulationDone: "Question routee vers simulation.",
    routeCopilotDone: "Question routee vers copilote.",
    builderOpsKicker: "Operations du builder",
    builderOpsTitle: "Pilotage AI Builder",
    builderRoute: "Dernier routage",
    builderLatency: "Latence",
    builderTables: "Tables utilisees",
    builderQueries: "Requetes",
    builderRouteEmpty: "Aucune action routee pour le moment.",
    builderStudioTitle: "Studio Builder IA",
    builderStudioCopy: "Construis les briques avancees: SQL, jointures, couche semantique, workflows, policies, observabilite et gouvernance.",
    builderStudioKicker: "Studio Builder IA",
    builderStudioResultTitle: "Briques du builder",
    runJoinAssistant: "Analyser les jointures",
    runSemanticLayer: "Construire la couche semantique",
    runPrepAgent: "Lancer le prep agent",
    runWorkflowBuilder: "Construire le workflow",
    joinAssistantTitle: "Assistant de jointure",
    semanticLayerTitle: "Couche semantique",
    prepAgentTitle: "Agent de preparation",
    workflowBuilderTitle: "Builder de workflow decisionnel",
    quantOptimizerTitle: "Optimiseur quantitatif",
    observabilityTitle: "Console d observabilite",
    constraintSolverTitle: "Solveur de contraintes",
    experimentDesignerTitle: "Designer d experimentations",
    evaluationConsoleTitle: "Console d evaluation",
    policyEngineTitle: "Moteur de policies",
    semanticKpiRegistryTitle: "Registre semantique KPI",
    orchestrationViewTitle: "Vue d orchestration des agents",
    builderEmpty: "Charge un dataset pour activer ce module.",
    workflowGoalPricing: "Decision tarifaire",
    workflowGoalDiagnosis: "Diagnostic",
    workflowGoalMarketing: "Optimisation marketing",
    workflowGoalSegment: "Priorisation segment",
    readinessScore: "Score de preparation",
    recommendedNextStep: "Prochaine etape recommandee",
    automationPotential: "Potentiel d automatisation",
    blockers: "Blocages",
    runQuantOptimizer: "Lancer l optimizer",
    runConstraintSolver: "Lancer le constraint solver",
    runExperimentDesigner: "Construire les experiments",
    runEvaluationConsole: "Rafraichir l evaluation",
    runPolicyEngine: "Lancer le policy engine",
    runSemanticKpiRegistry: "Construire le registre KPI",
    runOrchestrationView: "Voir l orchestration",
    optimizerPrediction: "Maximiser la prediction",
    optimizerEfficiency: "Maximiser l efficience",
    platformTitle: "Plateforme et gouvernance",
    platformCopy: "Cree un workspace, connecte des sources, exporte des artefacts et ajoute une validation humaine.",
    platformKicker: "Plateforme",
    platformResultTitle: "Espace de travail et gouvernance",
    createUser: "Creer l utilisateur",
    createProject: "Creer le projet",
    connectImportCsv: "Connecter et importer",
    exportWorkflowArtifact: "Exporter le workflow",
    exportPolicyArtifact: "Exporter la policy",
    requestApproval: "Demander une validation",
    approveLatest: "Approuver la derniere",
    refreshPlatform: "Rafraichir la gouvernance",
    workspaceOwnerPlaceholder: "Nom du builder",
    projectNamePlaceholder: "Nom du projet",
    connectorNamePlaceholder: "Nom du connecteur",
    connectorUrlPlaceholder: "URL CSV publique ou chemin sqlite",
    approvalTitlePlaceholder: "Nom de la validation",
    platformWorkspaceTitle: "Espace de travail",
    platformConnectorTitle: "Connecteurs",
    platformExportTitle: "Artefacts exportes",
    platformApprovalTitle: "Validations humaines",
    platformEmpty: "Aucun element plateforme pour le moment.",
    userCreated: "Utilisateur cree.",
    projectCreated: "Projet cree.",
    connectorImported: "Connecteur teste et dataset importe.",
    workflowExported: "Workflow exporte.",
    policyExported: "Policy exportee.",
    approvalRequested: "Validation demandee.",
    approvalApproved: "Validation approuvee.",
    personaTitle: "Parcours produit",
    personaCopy: "Choisis le profil acheteur et la couche produit a mettre en avant pendant la demo.",
    personaRevenue: "Revenue / Pricing",
    personaBuilder: "Builder IA",
    personaAnalytics: "Equipe data",
    surfaceDecision: "Copilote de decision",
    surfaceBuilder: "Studio Builder IA",
    surfaceGovernance: "Gouvernance",
    playbookTitle: "Playbooks demo",
    playbookCopy: "Applique un angle de demo concret pour guider la narration et pre-remplir les actions utiles.",
    playbookPricing: "Decision tarifaire",
    playbookGrowth: "Optimisation croissance",
    playbookExec: "Revue de direction",
    personaRevenueBrief: "Ideal pour un lead revenue, pricing ou croissance qui veut comprendre quoi faire ensuite et pourquoi.",
    personaBuilderBrief: "Ideal pour un consultant ou builder IA qui veut montrer les briques SQL, workflow, policy et gouvernance.",
    personaAnalyticsBrief: "Ideal pour une equipe data qui veut voir la couche gouvernance, les artefacts et la reutilisation du systeme.",
    playbookPricingStatus: "Playbook pricing charge.",
    playbookGrowthStatus: "Playbook croissance charge.",
    playbookExecStatus: "Playbook direction charge.",
    modeSummaryLabel: "Vue active",
    modeSummaryDecisionTitle: "Copilote de decision",
    modeSummaryDecisionCopy: "Vue dirigeant pour comprendre quoi faire, pourquoi, et avec quel niveau de confiance.",
    modeSummaryBuilderTitle: "Studio Builder IA",
    modeSummaryBuilderCopy: "Vue outillage pour montrer SQL, workflows, experimentation, observabilite et orchestration.",
    modeSummaryGovernanceTitle: "Gouvernance",
    modeSummaryGovernanceCopy: "Vue plateforme pour montrer projets, connecteurs, exports, validations humaines et traçabilite.",
    tabOverview: "Vue d ensemble",
    tabInsights: "Insights",
    tabModeling: "Modele et scenarios",
    tabActions: "Actions et copilote",
    tabSql: "SQL et routage",
    tabStudio: "Briques builder",
    tabPlatform: "Plateforme",
    tabEvidence: "Preuves et donnees",
  },
  en: {
    heroEyebrow: "AI decision copilot",
    heroCopy: "An accelerator for AI decision copilots that turns business data into diagnosis, simulations, and defensible recommendations.",
    heroAudienceKicker: "Who it is for",
    heroAudienceTitle: "Revenue, pricing, growth, and AI consultants",
    heroAudienceCopy: "Built for teams that need to explain what changed, test scenarios, and recommend a clear next move.",
    heroValueKicker: "What it does",
    heroValueTitle: "Investigate, simulate, and decide with evidence",
    heroValueCopy: "The product combines analytics, SQL, scenarios, guardrails, evidence packs, and exports in one workflow.",
    heroModeKicker: "Two modes",
    heroModeTitle: "Decision Copilot + AI Builder Studio",
    heroModeCopy: "A simple layer for decision-making, and an advanced layer for building, governing, and exporting copilots.",
    heroUsecase1: "Pricing decision",
    heroUsecase2: "Revenue investigation",
    heroUsecase3: "Growth optimization",
    heroUsecase4: "AI Builder workflows",
    controlsTitle: "Get started",
    controlsCopy: "Load a revenue demo or upload a CSV to activate a full decision copilot workflow.",
    workflowLoad: "Load data",
    workflowInsights: "Review insights",
    workflowTrain: "Train model",
    workflowSimulate: "Simulate",
    workflowDecide: "Decide",
    salesDemo: "Load sales demo",
    marketingDemo: "Load marketing demo",
    upload: "Upload a CSV",
    noData: "No dataset loaded yet.",
    ready: "Ready for a client demo",
    emptyTitle: "Load a dataset to activate the decision copilot.",
    emptyCopy: "You will then see prioritized insights, scenarios, recommendations, and the AI Builder studio.",
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
    modeLabel: "Positioning",
    modeValue: "Decision copilot accelerator",
    noAnswer: "Ask a question to display the copilot answer.",
    noTraining: "Train a model to display predictive signals.",
    exportTitle: "Executive report",
    exportCopy: "Export an HTML summary you can share in a client or management review.",
    exportReport: "Export report",
    exportReady: "Report exported",
    queryTitle: "Ask the data",
    queryPlaceholder: "What is the average revenue by region?",
    queryRun: "Generate SQL",
    queryRoute: "Route the question",
    queryRouterCopy: "Automatically chooses between SQL, prediction, simulation, or copilot.",
    queryKicker: "AI Builder",
    queryResultTitle: "Natural language to SQL",
    queryEmpty: "Ask a question about the data to display the generated SQL, the result, and the explanation.",
    querySql: "Generated SQL",
    queryRows: "Returned rows",
    queryWarning: "Warnings",
    queryExplain: "Explain this SQL",
    queryExplainDone: "SQL explanation updated.",
    queryExport: "Export CSV",
    queryExportDone: "SQL result exported as CSV.",
    queryHistoryKicker: "History",
    queryHistoryTitle: "Query history",
    queryHistoryEmpty: "Executed SQL queries will appear here.",
    queryHistoryReplay: "Replay",
    routeSqlDone: "Question routed to SQL.",
    routePredictionDone: "Question routed to prediction.",
    routeSimulationDone: "Question routed to simulation.",
    routeCopilotDone: "Question routed to copilot.",
    builderOpsKicker: "Builder ops",
    builderOpsTitle: "AI Builder control panel",
    builderRoute: "Last route",
    builderLatency: "Latency",
    builderTables: "Used tables",
    builderQueries: "Queries",
    builderRouteEmpty: "No routed action yet.",
    builderStudioTitle: "AI Builder Studio",
    builderStudioCopy: "Build advanced layers: SQL, joins, semantic models, workflows, policies, observability, and governance.",
    builderStudioKicker: "AI Builder Studio",
    builderStudioResultTitle: "Builder modules",
    runJoinAssistant: "Analyze joins",
    runSemanticLayer: "Build semantic layer",
    runPrepAgent: "Run prep agent",
    runWorkflowBuilder: "Build workflow",
    joinAssistantTitle: "Join assistant",
    semanticLayerTitle: "Semantic layer",
    prepAgentTitle: "Prep agent",
    workflowBuilderTitle: "Decision workflow builder",
    quantOptimizerTitle: "Quant optimizer",
    observabilityTitle: "Observability console",
    constraintSolverTitle: "Constraint solver",
    experimentDesignerTitle: "Experiment designer",
    evaluationConsoleTitle: "Evaluation console",
    policyEngineTitle: "Policy engine",
    semanticKpiRegistryTitle: "Semantic KPI registry",
    orchestrationViewTitle: "Agent orchestration view",
    builderEmpty: "Load a dataset to unlock this module.",
    workflowGoalPricing: "Pricing decision",
    workflowGoalDiagnosis: "Diagnosis",
    workflowGoalMarketing: "Marketing optimization",
    workflowGoalSegment: "Segment prioritization",
    readinessScore: "Readiness score",
    recommendedNextStep: "Recommended next step",
    automationPotential: "Automation potential",
    blockers: "Blockers",
    runQuantOptimizer: "Run optimizer",
    runConstraintSolver: "Run constraint solver",
    runExperimentDesigner: "Build experiments",
    runEvaluationConsole: "Refresh evaluation",
    runPolicyEngine: "Run policy engine",
    runSemanticKpiRegistry: "Build KPI registry",
    runOrchestrationView: "View orchestration",
    optimizerPrediction: "Maximize prediction",
    optimizerEfficiency: "Maximize efficiency",
    platformTitle: "Platform & Governance",
    platformCopy: "Create a workspace, connect a source, export artifacts, and request human approval.",
    platformKicker: "Platform",
    platformResultTitle: "Workspace and governance",
    createUser: "Create user",
    createProject: "Create project",
    connectImportCsv: "Connect and import",
    exportWorkflowArtifact: "Export workflow",
    exportPolicyArtifact: "Export policy",
    requestApproval: "Request approval",
    approveLatest: "Approve latest",
    refreshPlatform: "Refresh governance",
    workspaceOwnerPlaceholder: "Builder name",
    projectNamePlaceholder: "Project name",
    connectorNamePlaceholder: "Connector name",
    connectorUrlPlaceholder: "Public CSV URL or sqlite path",
    approvalTitlePlaceholder: "Approval title",
    platformWorkspaceTitle: "Workspace",
    platformConnectorTitle: "Connectors",
    platformExportTitle: "Exported artifacts",
    platformApprovalTitle: "Human approvals",
    platformEmpty: "No platform items yet.",
    userCreated: "User created.",
    projectCreated: "Project created.",
    connectorImported: "Connector tested and dataset imported.",
    workflowExported: "Workflow exported.",
    policyExported: "Policy exported.",
    approvalRequested: "Approval requested.",
    approvalApproved: "Approval approved.",
    personaTitle: "Product path",
    personaCopy: "Choose the buyer profile and the product layer to highlight during the demo.",
    personaRevenue: "Revenue / Pricing",
    personaBuilder: "AI Builder",
    personaAnalytics: "Analytics team",
    surfaceDecision: "Decision Copilot",
    surfaceBuilder: "AI Builder Studio",
    surfaceGovernance: "Governance",
    playbookTitle: "Demo playbooks",
    playbookCopy: "Apply a concrete demo angle to guide the story and prefill the right actions.",
    playbookPricing: "Pricing decision",
    playbookGrowth: "Growth optimization",
    playbookExec: "Executive review",
    personaRevenueBrief: "Best for revenue, pricing, and growth leads who need a clear next action with evidence.",
    personaBuilderBrief: "Best for consultants and AI builders who want to demo SQL, workflows, policies, and governance.",
    personaAnalyticsBrief: "Best for analytics teams that care about governance, exported artifacts, and reusable decision workflows.",
    playbookPricingStatus: "Pricing playbook loaded.",
    playbookGrowthStatus: "Growth playbook loaded.",
    playbookExecStatus: "Executive playbook loaded.",
    modeSummaryLabel: "Active view",
    modeSummaryDecisionTitle: "Decision Copilot",
    modeSummaryDecisionCopy: "Executive reading layer to understand what to do, why it matters, and how confident the system is.",
    modeSummaryBuilderTitle: "AI Builder Studio",
    modeSummaryBuilderCopy: "Builder layer to demo SQL, workflows, experimentation, observability, and orchestration.",
    modeSummaryGovernanceTitle: "Governance",
    modeSummaryGovernanceCopy: "Platform layer to demo projects, connectors, exports, approvals, and traceability.",
    tabOverview: "Overview",
    tabInsights: "Insights",
    tabModeling: "Prediction and scenarios",
    tabActions: "Actions and copilot",
    tabSql: "SQL and routing",
    tabStudio: "Builder modules",
    tabPlatform: "Platform",
    tabEvidence: "Evidence and data",
  },
};

const $ = (id) => document.getElementById(id);

function currentCopy() {
  return copy[state.lang];
}

function routeLockedSurface() {
  return ROUTE_PATHS[state.routePage] ? state.routePage : null;
}

function surfaceHref(mode, sectionId = null) {
  const path = ROUTE_PATHS[mode] || ROUTE_PATHS.decision;
  return sectionId ? `${path}#${sectionId}` : path;
}

function routeTheme() {
  const c = currentCopy();
  const themes = {
    decision: {
      heroTitle: "AI Data Investigator",
      heroEyebrow: state.lang === "fr" ? "Copilote de decision" : "Decision copilot",
      heroCopy: state.lang === "fr"
        ? "Une interface dirigeant pour comprendre ce qui change, tester des scenarios et recommander une action claire avec niveau de confiance."
        : "An executive layer to understand what changed, test scenarios, and recommend a clear next action with confidence.",
      audienceTitle: state.lang === "fr" ? "Revenue, pricing et croissance" : "Revenue, pricing, and growth teams",
      audienceCopy: state.lang === "fr"
        ? "Pour les equipes qui doivent arbitrer vite entre prix, demande, campagne et priorites commerciales."
        : "Built for teams that need to arbitrate quickly between pricing, demand, campaigns, and revenue priorities.",
      valueTitle: state.lang === "fr" ? "Investiguer, simuler, decider" : "Investigate, simulate, decide",
      valueCopy: state.lang === "fr"
        ? "La page met l accent sur les signaux, la simulation, la recommandation et l evidence pack."
        : "This page prioritizes signals, simulation, recommendation, and the evidence pack.",
      modeTitle: state.lang === "fr" ? "Vue metier prioritaire" : "Primary business view",
      modeCopy: state.lang === "fr"
        ? "Le flux va du chargement des donnees a la decision recommandee."
        : "The flow goes from loading data to a recommended decision.",
      usecases: [
        c.heroUsecase1,
        c.heroUsecase2,
        c.heroUsecase3,
        state.lang === "fr" ? "Recommandation board-ready" : "Board-ready recommendation",
      ],
      controlsTitle: state.lang === "fr" ? "Demarrer une analyse metier" : "Start a business analysis",
      controlsCopy: state.lang === "fr"
        ? "Charge une demo ou importe un CSV pour obtenir une lecture executive du signal, du risque et de la prochaine action."
        : "Load a demo or upload a CSV to get an executive read on signal, risk, and next action.",
      emptyTitle: state.lang === "fr" ? "Charge un dataset pour activer la vue decision." : "Load a dataset to activate the decision view.",
      emptyCopy: state.lang === "fr"
        ? "Tu verras ensuite la synthese de decision, les insights, les scenarios et les actions recommandees."
        : "You will then see the decision summary, insights, scenarios, and recommended actions.",
      workflowVisible: true,
    },
    builder: {
      heroTitle: state.lang === "fr" ? "Studio Builder IA" : "AI Builder Studio",
      heroEyebrow: state.lang === "fr" ? "Studio Builder IA" : "AI Builder Studio",
      heroCopy: state.lang === "fr"
        ? "Une page outillage pour construire des workflows decisionnels avec SQL, agents, preparation, orchestration et evaluation."
        : "A builder page for assembling decision workflows with SQL, agents, preparation, orchestration, and evaluation.",
      audienceTitle: state.lang === "fr" ? "Consultants IA et builders" : "AI consultants and builders",
      audienceCopy: state.lang === "fr"
        ? "Pour demonstrer rapidement un accelerateur de copilotes analytiques et gouvernes."
        : "Designed to quickly demonstrate an accelerator for governed analytical copilots.",
      valueTitle: state.lang === "fr" ? "Interroger, assembler, observer" : "Query, assemble, observe",
      valueCopy: state.lang === "fr"
        ? "La page met l accent sur SQL, les briques builder, le routage et l orchestration."
        : "This page focuses on SQL, builder modules, routing, and orchestration.",
      modeTitle: state.lang === "fr" ? "Vue builder prioritaire" : "Primary builder view",
      modeCopy: state.lang === "fr"
        ? "Le flux va de la question SQL au workflow et aux agents."
        : "The flow goes from SQL questions to workflows and agents.",
      usecases: [
        state.lang === "fr" ? "SQL genere" : "Generated SQL",
        state.lang === "fr" ? "Jointures assistees" : "Guided joins",
        state.lang === "fr" ? "Prep agent" : "Prep agent",
        state.lang === "fr" ? "Workflow builder" : "Workflow builder",
      ],
      controlsTitle: state.lang === "fr" ? "Charger des datasets a builder" : "Load datasets to build with",
      controlsCopy: state.lang === "fr"
        ? "Charge une demo ou importe un CSV avant de lancer SQL, jointures, prep agent et workflow."
        : "Load a demo or upload a CSV before launching SQL, joins, prep agents, and workflows.",
      emptyTitle: state.lang === "fr" ? "Charge un dataset pour activer le studio builder." : "Load a dataset to activate the builder studio.",
      emptyCopy: state.lang === "fr"
        ? "Tu pourras ensuite poser des questions SQL, construire les briques et observer le routage."
        : "You will then be able to ask SQL questions, build modules, and observe routing.",
      workflowVisible: false,
    },
    governance: {
      heroTitle: state.lang === "fr" ? "Gouvernance des copilotes" : "Copilot Governance",
      heroEyebrow: state.lang === "fr" ? "Gouvernance des copilotes" : "Copilot governance",
      heroCopy: state.lang === "fr"
        ? "Une page plateforme pour cadrer projets, connecteurs, artefacts, validations humaines et reutilisation des workflows."
        : "A platform page to manage projects, connectors, artifacts, human approvals, and reusable workflows.",
      audienceTitle: state.lang === "fr" ? "Equipe data et analytics" : "Data and analytics teams",
      audienceCopy: state.lang === "fr"
        ? "Pour montrer la couche gouvernance sans noyer le lecteur dans le detail analytique."
        : "A focused governance layer without overwhelming the reader with analytical detail.",
      valueTitle: state.lang === "fr" ? "Connecter, valider, tracer" : "Connect, approve, trace",
      valueCopy: state.lang === "fr"
        ? "La page met l accent sur la gouvernance des runs, des connecteurs et des exports."
        : "This page prioritizes governance of runs, connectors, and exported artifacts.",
      modeTitle: state.lang === "fr" ? "Vue gouvernance prioritaire" : "Primary governance view",
      modeCopy: state.lang === "fr"
        ? "Le flux va du projet a la validation humaine."
        : "The flow goes from project setup to human approval.",
      usecases: [
        state.lang === "fr" ? "Workspaces" : "Workspaces",
        state.lang === "fr" ? "Connecteurs" : "Connectors",
        state.lang === "fr" ? "Exports" : "Exports",
        state.lang === "fr" ? "Validations humaines" : "Human approvals",
      ],
      controlsTitle: state.lang === "fr" ? "Charger ou connecter une source" : "Load or connect a source",
      controlsCopy: state.lang === "fr"
        ? "Charge une demo ou connecte une source avant de configurer le workspace et les validations."
        : "Load a demo or connect a source before configuring the workspace and approvals.",
      emptyTitle: state.lang === "fr" ? "Charge un dataset ou connecte une source pour activer la gouvernance." : "Load a dataset or connect a source to activate governance.",
      emptyCopy: state.lang === "fr"
        ? "Tu verras ensuite les projets, connecteurs, artefacts exportes et validations humaines."
        : "You will then see projects, connectors, exported artifacts, and human approvals.",
      workflowVisible: false,
    },
  };
  return themes[state.surfaceMode] || themes.decision;
}

function syncRouteSurface() {
  const locked = routeLockedSurface();
  if (!locked) return;
  state.surfaceMode = locked;
  if (!state.routePresetApplied) {
    state.marketProfile = ROUTE_DEFAULT_PROFILES[locked] || state.marketProfile;
    state.routePresetApplied = true;
  }
  const hashSection = window.location.hash.replace("#", "");
  if (!hashSection) return;
  const configs = currentSurfaceTabConfig()[locked] || [];
  const matching = configs.find((tab) => tab.sections.includes(hashSection));
  if (matching) {
    state.surfaceSubtabs[locked] = matching.key;
  }
}

function renderPageNav() {
  const c = currentCopy();
  $("nav-decision").textContent = c.surfaceDecision;
  $("nav-builder").textContent = c.surfaceBuilder;
  $("nav-governance").textContent = c.surfaceGovernance;
  $("nav-decision").classList.toggle("active", state.surfaceMode === "decision");
  $("nav-builder").classList.toggle("active", state.surfaceMode === "builder");
  $("nav-governance").classList.toggle("active", state.surfaceMode === "governance");
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
  await refreshDatasets();
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
  state.sqlQuery = null;
  state.sqlHistory = [];
  state.focusedAnalysis = null;
  state.builderOps.usedTables = [];
  state.joinAssistant = null;
  state.semanticLayer = null;
  state.prepAgent = null;
  state.workflowBuilder = null;
  state.quantOptimizer = null;
  state.observability = null;
  state.constraintSolver = null;
  state.experimentDesigner = null;
  state.evaluationConsole = null;
  state.policyEngine = null;
  state.semanticKpiRegistry = null;
  state.orchestrationView = null;
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

async function refreshDatasets() {
  try {
    state.datasets = await api("/datasets");
  } catch (_error) {
    state.datasets = state.dataset ? [state.dataset] : [];
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

function downloadCsv(filename, rows, columns) {
  if (!rows?.length || !columns?.length) return;
  const escapeCell = (value) => `"${String(value ?? "").replace(/"/g, '""')}"`;
  const csv = [
    columns.map(escapeCell).join(","),
    ...rows.map((row) => columns.map((column) => escapeCell(row[column])).join(",")),
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function upsertSqlHistory(entry) {
  state.sqlHistory = [
    entry,
    ...state.sqlHistory.filter((item) => !(item.question === entry.question && item.sql === entry.sql)),
  ].slice(0, 6);
}

function classifyQuestion(question) {
  const lower = question.toLowerCase();
  if (/(average|avg|mean|sum|total|count|top|list|show|breakdown|group by|combien|moyen|moyenne|total|somme|liste|montre)/.test(lower)) {
    return "sql";
  }
  if (/(predict|prediction|forecast|forecasting|driver|driver[s]?|prevoir|predire|prediction|modele)/.test(lower)) {
    return "prediction";
  }
  if (/(simulate|simulation|scenario|what if|what-if|si on|impact|increase price|decrease price|augmenter le prix|baisser le prix)/.test(lower)) {
    return "simulation";
  }
  return "copilot";
}

function renderStaticCopy() {
  const c = currentCopy();
  const theme = routeTheme();
  const baselineMode = $("baseline-mode-select")?.value || "reference_row";
  const referenceIndex = $("reference-index-input")?.value || "0";
  const workflowGoal = $("workflow-goal-select")?.value || "pricing_decision";
  const optimizerGoal = $("optimizer-objective-select")?.value || "maximize_prediction";
  document.documentElement.lang = state.lang;
  $("hero-title").textContent = theme.heroTitle;
  $("hero-eyebrow").textContent = theme.heroEyebrow;
  $("hero-copy").textContent = theme.heroCopy;
  $("positioning-audience-kicker").textContent = c.heroAudienceKicker;
  $("positioning-audience-title").textContent = theme.audienceTitle;
  $("positioning-audience-copy").textContent = theme.audienceCopy;
  $("positioning-value-kicker").textContent = c.heroValueKicker;
  $("positioning-value-title").textContent = theme.valueTitle;
  $("positioning-value-copy").textContent = theme.valueCopy;
  $("positioning-mode-kicker").textContent = c.heroModeKicker;
  $("positioning-mode-title").textContent = theme.modeTitle;
  $("positioning-mode-copy").textContent = theme.modeCopy;
  $("hero-usecase-1").textContent = theme.usecases[0];
  $("hero-usecase-2").textContent = theme.usecases[1];
  $("hero-usecase-3").textContent = theme.usecases[2];
  $("hero-usecase-4").textContent = theme.usecases[3];
  $("persona-title").textContent = c.personaTitle;
  $("persona-copy").textContent = c.personaCopy;
  $("persona-revenue").textContent = c.personaRevenue;
  $("persona-builder").textContent = c.personaBuilder;
  $("persona-analytics").textContent = c.personaAnalytics;
  $("surface-decision").textContent = c.surfaceDecision;
  $("surface-builder").textContent = c.surfaceBuilder;
  $("surface-governance").textContent = c.surfaceGovernance;
  $("dashboard-tab-decision").textContent = c.surfaceDecision;
  $("dashboard-tab-builder").textContent = c.surfaceBuilder;
  $("dashboard-tab-governance").textContent = c.surfaceGovernance;
  $("playbook-title").textContent = c.playbookTitle;
  $("playbook-copy").textContent = c.playbookCopy;
  $("playbook-pricing").textContent = c.playbookPricing;
  $("playbook-growth").textContent = c.playbookGrowth;
  $("playbook-exec").textContent = c.playbookExec;
  $("controls-title").textContent = theme.controlsTitle;
  $("controls-copy").textContent = theme.controlsCopy;
  $("query-title").textContent = c.queryTitle;
  $("sql-question-input").placeholder = c.queryPlaceholder;
  $("run-sql-query").textContent = c.queryRun;
  $("route-query").textContent = c.queryRoute;
  $("query-router-copy").textContent = c.queryRouterCopy;
  $("builder-studio-title").textContent = c.builderStudioTitle;
  $("builder-studio-copy").textContent = c.builderStudioCopy;
  $("run-join-assistant").textContent = c.runJoinAssistant;
  $("run-semantic-layer").textContent = c.runSemanticLayer;
  $("run-prep-agent").textContent = c.runPrepAgent;
  $("run-workflow-builder").textContent = c.runWorkflowBuilder;
  $("run-quant-optimizer").textContent = c.runQuantOptimizer;
  $("run-constraint-solver").textContent = c.runConstraintSolver;
  $("run-experiment-designer").textContent = c.runExperimentDesigner;
  $("run-evaluation-console").textContent = c.runEvaluationConsole;
  $("run-policy-engine").textContent = c.runPolicyEngine;
  $("run-semantic-kpi-registry").textContent = c.runSemanticKpiRegistry;
  $("run-orchestration-view").textContent = c.runOrchestrationView;
  $("platform-title").textContent = c.platformTitle;
  $("platform-copy").textContent = c.platformCopy;
  $("create-user").textContent = c.createUser;
  $("create-project").textContent = c.createProject;
  $("connect-import-csv").textContent = c.connectImportCsv;
  $("export-workflow-artifact").textContent = c.exportWorkflowArtifact;
  $("export-policy-artifact").textContent = c.exportPolicyArtifact;
  $("request-approval").textContent = c.requestApproval;
  $("approve-latest").textContent = c.approveLatest;
  $("refresh-platform").textContent = c.refreshPlatform;
  $("workspace-owner-input").placeholder = c.workspaceOwnerPlaceholder;
  $("project-name-input").placeholder = c.projectNamePlaceholder;
  $("connector-name-input").placeholder = c.connectorNamePlaceholder;
  $("connector-url-input").placeholder = c.connectorUrlPlaceholder;
  $("approval-title-input").placeholder = c.approvalTitlePlaceholder;
  $("export-title").textContent = c.exportTitle;
  $("export-copy").textContent = c.exportCopy;
  $("export-report").textContent = c.exportReport;
  $("load-sales").textContent = c.salesDemo;
  $("load-marketing").textContent = c.marketingDemo;
  $("upload-label").textContent = c.upload;
  $("empty-eyebrow").textContent = c.ready;
  $("empty-title").textContent = theme.emptyTitle;
  $("empty-copy").textContent = theme.emptyCopy;
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
  $("query-kicker").textContent = c.queryKicker;
  $("query-result-title").textContent = c.queryResultTitle;
  $("explain-sql").textContent = c.queryExplain;
  $("export-query-csv").textContent = c.queryExport;
  $("query-history-kicker").textContent = c.queryHistoryKicker;
  $("query-history-title").textContent = c.queryHistoryTitle;
  $("builder-ops-kicker").textContent = c.builderOpsKicker;
  $("builder-ops-title").textContent = c.builderOpsTitle;
  $("builder-studio-kicker").textContent = c.builderStudioKicker;
  $("builder-studio-result-title").textContent = c.builderStudioResultTitle;
  $("platform-kicker").textContent = c.platformKicker;
  $("platform-result-title").textContent = c.platformResultTitle;
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
  $("band-mode-value").textContent = `${c.modeValue} · ${state.surfaceMode === "decision" ? c.surfaceDecision : state.surfaceMode === "builder" ? c.surfaceBuilder : c.surfaceGovernance}`;
  $("lang-fr").classList.toggle("active", state.lang === "fr");
  $("lang-en").classList.toggle("active", state.lang === "en");
  $("workflow-goal-select").innerHTML = `
    <option value="pricing_decision">${c.workflowGoalPricing}</option>
    <option value="diagnosis">${c.workflowGoalDiagnosis}</option>
    <option value="marketing_optimization">${c.workflowGoalMarketing}</option>
    <option value="segment_prioritization">${c.workflowGoalSegment}</option>
  `;
  $("workflow-goal-select").value = workflowGoal;
  $("optimizer-objective-select").innerHTML = `
    <option value="maximize_prediction">${c.optimizerPrediction}</option>
    <option value="maximize_efficiency">${c.optimizerEfficiency}</option>
  `;
  $("optimizer-objective-select").value = optimizerGoal;
  if (!state.dataset) {
    setStatus(c.noData);
  }
}

function renderWorkflow() {
  const c = currentCopy();
  if (!routeTheme().workflowVisible) {
    $("workflow-strip").hidden = true;
    $("workflow-steps").innerHTML = "";
    return;
  }
  $("workflow-strip").hidden = false;
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

function renderPersonaBrief() {
  const c = currentCopy();
  const briefMap = {
    revenue: c.personaRevenueBrief,
    builder: c.personaBuilderBrief,
    analytics: c.personaAnalyticsBrief,
  };
  $("persona-brief").innerHTML = `<strong>${state.surfaceMode === "decision" ? c.surfaceDecision : state.surfaceMode === "builder" ? c.surfaceBuilder : c.surfaceGovernance}</strong><p>${briefMap[state.marketProfile] || c.personaRevenueBrief}</p>`;
  $("persona-revenue").classList.toggle("active", state.marketProfile === "revenue");
  $("persona-builder").classList.toggle("active", state.marketProfile === "builder");
  $("persona-analytics").classList.toggle("active", state.marketProfile === "analytics");
  $("surface-decision").classList.toggle("active", state.surfaceMode === "decision");
  $("surface-builder").classList.toggle("active", state.surfaceMode === "builder");
  $("surface-governance").classList.toggle("active", state.surfaceMode === "governance");
  $("dashboard-tab-decision").classList.toggle("active", state.surfaceMode === "decision");
  $("dashboard-tab-builder").classList.toggle("active", state.surfaceMode === "builder");
  $("dashboard-tab-governance").classList.toggle("active", state.surfaceMode === "governance");
}

function renderModeSummary() {
  const c = currentCopy();
  const mapping = {
    decision: {
      title: c.modeSummaryDecisionTitle,
      copy: c.modeSummaryDecisionCopy,
    },
    builder: {
      title: c.modeSummaryBuilderTitle,
      copy: c.modeSummaryBuilderCopy,
    },
    governance: {
      title: c.modeSummaryGovernanceTitle,
      copy: c.modeSummaryGovernanceCopy,
    },
  };
  const current = mapping[state.surfaceMode] || mapping.decision;
  $("dashboard-mode-label").textContent = c.modeSummaryLabel;
  $("dashboard-mode-title").textContent = current.title;
  $("dashboard-mode-copy").textContent = current.copy;
}

function applyRouteLayout() {
  const locked = routeLockedSurface();
  const visiblePanels = {
    decision: ["persona-panel", "playbook-panel", "controls-panel", "copilot-panel", "export-panel", "analysis-panel"],
    builder: ["persona-panel", "controls-panel", "query-panel", "builder-panel", "export-panel"],
    governance: ["persona-panel", "controls-panel", "platform-panel", "export-panel"],
  };
  const allowed = new Set(visiblePanels[state.surfaceMode] || visiblePanels.decision);
  ["persona-panel", "playbook-panel", "controls-panel", "copilot-panel", "query-panel", "builder-panel", "platform-panel", "export-panel", "analysis-panel"].forEach((panelId) => {
    $(panelId).hidden = !(allowed.has(panelId));
  });
  $("surface-mode-row").hidden = Boolean(locked);
  $("dashboard-tab-group").hidden = Boolean(locked);
}

function currentSurfaceTabConfig() {
  const c = currentCopy();
  return {
    decision: [
      { key: "overview", label: c.tabOverview, sections: ["section-decision-summary", "section-confidence", "section-snapshot"] },
      { key: "insights", label: c.tabInsights, sections: ["section-insights", "section-suggestions", "section-charts"] },
      { key: "modeling", label: c.tabModeling, sections: ["section-prediction", "section-simulation", "section-engine"] },
      { key: "actions", label: c.tabActions, sections: ["section-actions", "section-copilot", "section-evidence"] },
    ],
    builder: [
      { key: "sql", label: c.tabSql, sections: ["section-query"] },
      { key: "studio", label: c.tabStudio, sections: ["section-builder-studio"] },
    ],
    governance: [
      { key: "platform", label: c.tabPlatform, sections: ["section-platform"] },
      { key: "evidence", label: c.tabEvidence, sections: ["section-snapshot", "section-evidence"] },
    ],
  };
}

function renderContentTabs() {
  const configs = currentSurfaceTabConfig()[state.surfaceMode] || [];
  $("content-tabs").innerHTML = configs
    .map(
      (tab) => `
        <button
          class="content-tab-btn ${state.surfaceSubtabs[state.surfaceMode] === tab.key ? "active" : ""}"
          type="button"
          data-surface-tab="${tab.key}"
        >
          ${tab.label}
        </button>
      `,
    )
    .join("");
}

function applySurfaceMode() {
  const configs = currentSurfaceTabConfig()[state.surfaceMode] || [];
  const activeTab = state.surfaceSubtabs[state.surfaceMode];
  const allowedSections = new Set((configs.find((tab) => tab.key === activeTab)?.sections || []));
  document.querySelectorAll("#dashboard > section").forEach((section) => {
    if (!section.id) return;
    const allowed =
      state.surfaceMode === "decision"
        ? section.classList.contains("surface-decision")
        : state.surfaceMode === "builder"
          ? section.classList.contains("surface-builder")
          : section.classList.contains("surface-governance");
    section.hidden = !(allowed && allowedSections.has(section.id));
  });
}

function focusSection(sectionId = null) {
  if (!sectionId) {
    $("dashboard-tabs")?.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }
  const node = $(sectionId);
  if (!node || node.hidden) return;
  node.scrollIntoView({ behavior: "smooth", block: "start" });
}

function switchSurface(mode, sectionId = null) {
  state.surfaceMode = mode;
  if (sectionId) {
    const configs = currentSurfaceTabConfig()[mode] || [];
    const matching = configs.find((tab) => tab.sections.includes(sectionId));
    if (matching) {
      state.surfaceSubtabs[mode] = matching.key;
    }
  }
  render();
  window.setTimeout(() => focusSection(sectionId), 80);
}

function goToSurface(mode, sectionId = null) {
  const locked = routeLockedSurface();
  if (locked && mode !== locked) {
    window.location.href = surfaceHref(mode, sectionId);
    return;
  }
  switchSurface(mode, sectionId);
}

function focusCurrentSubtab() {
  const configs = currentSurfaceTabConfig()[state.surfaceMode] || [];
  const activeTab = state.surfaceSubtabs[state.surfaceMode];
  const firstSection = configs.find((tab) => tab.key === activeTab)?.sections?.[0];
  focusSection(firstSection || null);
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

function renderSqlQuery() {
  const c = currentCopy();
  if (!state.sqlQuery) {
    $("query-result").innerHTML = `<div class="answer-card">${c.queryEmpty}</div>`;
    return;
  }
  const rows = state.sqlQuery.result_preview || [];
  let tableHtml = "";
  if (rows.length) {
    const columns = state.sqlQuery.columns || Object.keys(rows[0]);
    const head = `<tr>${columns.map((col) => `<th>${col}</th>`).join("")}</tr>`;
    const body = rows
      .slice(0, 12)
      .map((row) => `<tr>${columns.map((col) => `<td>${row[col] ?? ""}</td>`).join("")}</tr>`)
      .join("");
    tableHtml = `<div class="table-wrap"><table><thead>${head}</thead><tbody>${body}</tbody></table></div>`;
  }
  const warnings = (state.sqlQuery.warnings || []).length
    ? `<article class="answer-card"><strong>${c.queryWarning}</strong><p>${state.sqlQuery.warnings.join("<br />")}</p></article>`
    : "";
  $("query-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.querySql}</strong>
      <pre class="sql-block">${state.sqlQuery.sql}</pre>
    </article>
    <article class="answer-card">
      <strong>${c.queryRows}</strong>
      <p>${state.sqlQuery.row_count}</p>
      <p>${state.sqlQuery.explanation}</p>
    </article>
    ${warnings}
    ${tableHtml}
  `;
}

function renderSqlHistory() {
  const c = currentCopy();
  if (!state.sqlHistory.length) {
    $("query-history").innerHTML = `<div class="answer-card">${c.queryHistoryEmpty}</div>`;
    return;
  }
  $("query-history").innerHTML = state.sqlHistory
    .map(
      (item, index) => `
        <article class="history-item">
          <div>
            <strong>${item.question}</strong>
            <div class="small-meta">${item.row_count} ${c.rows.toLowerCase()}</div>
          </div>
          <button class="ghost-btn history-replay-btn" type="button" data-history-index="${index}">
            ${c.queryHistoryReplay}
          </button>
        </article>
      `,
    )
    .join("");
}

function renderBuilderOps() {
  const c = currentCopy();
  const route = state.builderOps.lastRoute || c.builderRouteEmpty;
  const latency = state.builderOps.lastLatencyMs ? `${state.builderOps.lastLatencyMs} ms` : "-";
  const tables = state.builderOps.usedTables.length ? state.builderOps.usedTables.join(", ") : "-";
  $("builder-ops").innerHTML = `
    <article class="metric-card">
      <div class="small-meta">${c.builderRoute}</div>
      <div class="metric-value builder-metric">${route}</div>
    </article>
    <article class="metric-card">
      <div class="small-meta">${c.builderLatency}</div>
      <div class="metric-value builder-metric">${latency}</div>
    </article>
    <article class="metric-card">
      <div class="small-meta">${c.builderTables}</div>
      <div class="builder-copy">${tables}</div>
    </article>
    <article class="metric-card">
      <div class="small-meta">${c.builderQueries}</div>
      <div class="metric-value builder-metric">${state.builderOps.queryCount}</div>
    </article>
  `;
}

function renderJoinAssistant() {
  const c = currentCopy();
  if (!state.joinAssistant) {
    $("join-assistant-result").innerHTML = `<div class="answer-card"><strong>${c.joinAssistantTitle}</strong><p>${c.builderEmpty}</p></div>`;
    return;
  }
  const candidate = state.joinAssistant.candidates?.[0];
  $("join-assistant-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.joinAssistantTitle}</strong>
      <p>${state.joinAssistant.recommended_next_step}</p>
      ${
        candidate
          ? `<p><strong>${candidate.filename}</strong><br />${candidate.merge_readiness} readiness • ${candidate.estimated_overlap_rows} overlap rows<br />${candidate.explanation}</p>`
          : ""
      }
    </article>
  `;
}

function renderSemanticLayer() {
  const c = currentCopy();
  if (!state.semanticLayer) {
    $("semantic-layer-result").innerHTML = `<div class="answer-card"><strong>${c.semanticLayerTitle}</strong><p>${c.builderEmpty}</p></div>`;
    return;
  }
  $("semantic-layer-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.semanticLayerTitle}</strong>
      <p><strong>Entities:</strong><br />${(state.semanticLayer.entities || []).join("<br />") || "-"}</p>
      <p><strong>Dimensions:</strong><br />${(state.semanticLayer.dimensions || []).join("<br />") || "-"}</p>
      <p><strong>Measures:</strong><br />${(state.semanticLayer.measures || []).join("<br />") || "-"}</p>
      <p><strong>KPI:</strong><br />${(state.semanticLayer.recommended_kpis || []).join("<br />") || "-"}</p>
    </article>
  `;
}

function renderPrepAgent() {
  const c = currentCopy();
  if (!state.prepAgent) {
    $("prep-agent-result").innerHTML = `<div class="answer-card"><strong>${c.prepAgentTitle}</strong><p>${c.builderEmpty}</p></div>`;
    return;
  }
  $("prep-agent-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.prepAgentTitle}</strong>
      <p><strong>${c.readinessScore}:</strong> ${state.prepAgent.readiness_score}</p>
      <p><strong>Cleanup:</strong><br />${(state.prepAgent.cleanup_tasks || []).map((item) => item.title).join("<br />") || "-"}</p>
      <p><strong>Features:</strong><br />${(state.prepAgent.feature_opportunities || []).map((item) => item.title).join("<br />") || "-"}</p>
      <p><strong>${c.recommendedNextStep}:</strong><br />${state.prepAgent.recommended_next_step}</p>
    </article>
  `;
}

function renderWorkflowBuilder() {
  const c = currentCopy();
  if (!state.workflowBuilder) {
    $("workflow-builder-result").innerHTML = `<div class="answer-card"><strong>${c.workflowBuilderTitle}</strong><p>${c.builderEmpty}</p></div>`;
    return;
  }
  $("workflow-builder-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.workflowBuilderTitle}</strong>
      <p>${state.workflowBuilder.goal}</p>
      <p>${(state.workflowBuilder.steps || []).map((step) => `${step.status.toUpperCase()} - ${step.title}`).join("<br />")}</p>
      <p><strong>${c.blockers}:</strong><br />${(state.workflowBuilder.blockers || []).join("<br />") || "-"}</p>
      <p><strong>${c.automationPotential}:</strong><br />${state.workflowBuilder.automation_potential}</p>
    </article>
  `;
}

function renderQuantOptimizer() {
  const c = currentCopy();
  if (!state.quantOptimizer) {
    $("quant-optimizer-result").innerHTML = `<div class="answer-card"><strong>${c.quantOptimizerTitle}</strong><p>${c.builderEmpty}</p></div>`;
    return;
  }
  $("quant-optimizer-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.quantOptimizerTitle}</strong>
      <p>${state.quantOptimizer.narrative}</p>
      <p><strong>Baseline:</strong> ${state.quantOptimizer.baseline_prediction}</p>
      <p><strong>Optimized:</strong> ${state.quantOptimizer.optimized_prediction}</p>
      <p><strong>Improvement:</strong> ${state.quantOptimizer.improvement}</p>
      <p><strong>Changes:</strong><br />${Object.entries(state.quantOptimizer.recommended_changes || {}).map(([key, value]) => `${key}: ${value}`).join("<br />") || "-"}</p>
    </article>
  `;
}

function renderObservability() {
  const c = currentCopy();
  if (!state.observability?.items?.length) {
    $("observability-result").innerHTML = `<div class="answer-card"><strong>${c.observabilityTitle}</strong><p>${c.builderEmpty}</p></div>`;
    return;
  }
  $("observability-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.observabilityTitle}</strong>
      <p>${state.observability.items
        .slice(0, 6)
        .map((item) => `[${item.route}] ${item.tool_name} - ${item.status} - ${item.detail}`)
        .join("<br />")}</p>
    </article>
  `;
}

function renderConstraintSolver() {
  const c = currentCopy();
  if (!state.constraintSolver) {
    $("constraint-solver-result").innerHTML = `<div class="answer-card"><strong>${c.constraintSolverTitle}</strong><p>${c.builderEmpty}</p></div>`;
    return;
  }
  $("constraint-solver-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.constraintSolverTitle}</strong>
      <p>${state.constraintSolver.rationale}</p>
      <p><strong>Changes:</strong><br />${Object.entries(state.constraintSolver.recommended_changes || {}).map(([key, value]) => `${key}: ${value}`).join("<br />") || "-"}</p>
      <p><strong>Constraints:</strong><br />${(state.constraintSolver.constraints_applied || []).join("<br />") || "-"}</p>
    </article>
  `;
}

function renderExperimentDesigner() {
  const c = currentCopy();
  if (!state.experimentDesigner) {
    $("experiment-designer-result").innerHTML = `<div class="answer-card"><strong>${c.experimentDesignerTitle}</strong><p>${c.builderEmpty}</p></div>`;
    return;
  }
  $("experiment-designer-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.experimentDesignerTitle}</strong>
      <p>${(state.experimentDesigner.recommendations || []).map((item) => `<strong>${item.title}</strong><br />${item.hypothesis}<br />Metric: ${item.primary_metric}<br />Guardrail: ${item.guardrail}`).join("<br /><br />")}</p>
    </article>
  `;
}

function renderEvaluationConsole() {
  const c = currentCopy();
  if (!state.evaluationConsole) {
    $("evaluation-console-result").innerHTML = `<div class="answer-card"><strong>${c.evaluationConsoleTitle}</strong><p>${c.builderEmpty}</p></div>`;
    return;
  }
  $("evaluation-console-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.evaluationConsoleTitle}</strong>
      <p>Total ops: ${state.evaluationConsole.total_operations}</p>
      <p>Success rate: ${state.evaluationConsole.success_rate_pct}%</p>
      <p>Fallback rate: ${state.evaluationConsole.fallback_rate_pct}%</p>
      <p>Top routes: ${(state.evaluationConsole.top_routes || []).join(", ") || "-"}</p>
      <p>${state.evaluationConsole.readiness_label}</p>
    </article>
  `;
}

function renderPolicyEngine() {
  const c = currentCopy();
  if (!state.policyEngine) {
    $("policy-engine-result").innerHTML = `<div class="answer-card"><strong>${c.policyEngineTitle}</strong><p>${c.builderEmpty}</p></div>`;
    return;
  }
  $("policy-engine-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.policyEngineTitle}</strong>
      <p>${state.policyEngine.recommended_action}</p>
      <p><strong>Guardrails:</strong><br />${(state.policyEngine.guardrails || []).join("<br />") || "-"}</p>
      <p><strong>Allowed:</strong><br />${(state.policyEngine.allowed_moves || []).join("<br />") || "-"}</p>
      <p><strong>Blocked:</strong><br />${(state.policyEngine.blocked_moves || []).join("<br />") || "-"}</p>
    </article>
  `;
}

function renderSemanticKpiRegistry() {
  const c = currentCopy();
  if (!state.semanticKpiRegistry) {
    $("semantic-kpi-registry-result").innerHTML = `<div class="answer-card"><strong>${c.semanticKpiRegistryTitle}</strong><p>${c.builderEmpty}</p></div>`;
    return;
  }
  $("semantic-kpi-registry-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.semanticKpiRegistryTitle}</strong>
      <p><strong>Default KPI:</strong> ${state.semanticKpiRegistry.recommended_default_kpi}</p>
      <p>${(state.semanticKpiRegistry.kpis || []).map((item) => `<strong>${item.name}</strong><br />${item.formula}<br />${item.business_use}`).join("<br /><br />")}</p>
    </article>
  `;
}

function renderOrchestrationView() {
  const c = currentCopy();
  if (!state.orchestrationView) {
    $("orchestration-view-result").innerHTML = `<div class="answer-card"><strong>${c.orchestrationViewTitle}</strong><p>${c.builderEmpty}</p></div>`;
    return;
  }
  $("orchestration-view-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.orchestrationViewTitle}</strong>
      <p>${state.orchestrationView.summary}</p>
      <p>${(state.orchestrationView.stages || []).map((item) => `${item.status.toUpperCase()} - ${item.stage} (${item.owner})`).join("<br />")}</p>
      <p><strong>Agents:</strong> ${(state.orchestrationView.active_agents || []).join(", ") || "-"}</p>
    </article>
  `;
}

function renderPlatformOverview() {
  const c = currentCopy();
  const overview = state.platformOverview;
  if (!overview) {
    const empty = `<div class="answer-card"><strong>${c.platformTitle}</strong><p>${c.platformEmpty}</p></div>`;
    $("workspace-result").innerHTML = empty;
    $("connector-platform-result").innerHTML = empty;
    $("artifact-export-result").innerHTML = empty;
    $("approval-result").innerHTML = empty;
    return;
  }

  const users = overview.users || [];
  const projects = overview.projects || [];
  const connectors = overview.connectors || [];
  const approvals = overview.approvals || [];
  const exportsList = overview.exports || [];

  $("workspace-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.platformWorkspaceTitle}</strong>
      <p><strong>Users:</strong> ${users.length}</p>
      <p><strong>Projects:</strong> ${projects.length}</p>
      <p>${users.slice(0, 3).map((item) => `${item.name} (${item.role})`).join("<br />") || "-"}</p>
      <p>${projects.slice(0, 3).map((item) => `${item.name}`).join("<br />") || "-"}</p>
    </article>
  `;

  $("connector-platform-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.platformConnectorTitle}</strong>
      <p><strong>Count:</strong> ${connectors.length}</p>
      <p>${connectors.slice(0, 3).map((item) => `${item.name}<br />${item.config_summary}`).join("<br /><br />") || "-"}</p>
      ${state.latestConnectorTest ? `<p><strong>Last test:</strong> ${state.latestConnectorTest.status} - ${state.latestConnectorTest.detail}</p>` : ""}
    </article>
  `;

  $("artifact-export-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.platformExportTitle}</strong>
      <p><strong>Count:</strong> ${exportsList.length}</p>
      <p>${exportsList.slice(0, 4).map((item) => `${item.artifact_type}: ${item.name}<br />${item.summary}`).join("<br /><br />") || "-"}</p>
    </article>
  `;

  $("approval-result").innerHTML = `
    <article class="answer-card">
      <strong>${c.platformApprovalTitle}</strong>
      <p><strong>Count:</strong> ${approvals.length}</p>
      <p>${approvals.slice(0, 4).map((item) => `${item.status.toUpperCase()} - ${item.title}<br />${item.summary}`).join("<br /><br />") || "-"}</p>
    </article>
  `;
}

function render() {
  syncRouteSurface();
  renderStaticCopy();
  renderPageNav();
  renderWorkflow();
  renderPersonaBrief();
  renderModeSummary();
  applyRouteLayout();
  const hasData = Boolean(state.dataset && state.profile && state.investigation);
  $("empty-state").hidden = hasData;
  $("dashboard-tabs").hidden = !hasData;
  $("content-tabs").hidden = !hasData;
  $("dashboard").hidden = !hasData;
  if (!hasData) {
    return;
  }
  renderContentTabs();
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
  renderSqlQuery();
  renderSqlHistory();
  renderBuilderOps();
  renderJoinAssistant();
  renderSemanticLayer();
  renderPrepAgent();
  renderWorkflowBuilder();
  renderQuantOptimizer();
  renderObservability();
  renderConstraintSolver();
  renderExperimentDesigner();
  renderEvaluationConsole();
  renderPolicyEngine();
  renderSemanticKpiRegistry();
  renderOrchestrationView();
  renderPlatformOverview();
  applySurfaceMode();
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
    const startedAt = performance.now();
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
    state.builderOps.lastRoute = "prediction";
    state.builderOps.lastLatencyMs = Math.round(performance.now() - startedAt);
    setStatus(currentCopy().trainingDone);
    await prepareDecisionEngine();
    goToSurface("decision", "section-prediction");
  } catch (error) {
    setStatus(`${currentCopy().connectError} ${error.message}`, true);
  }
}

async function runGuidedSimulation() {
  if (!state.dataset || !state.training) return;
  try {
    const startedAt = performance.now();
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
    state.builderOps.lastRoute = "simulation";
    state.builderOps.lastLatencyMs = Math.round(performance.now() - startedAt);
    setStatus(currentCopy().simulationReady);
    renderSimulation();
    goToSurface("decision", "section-simulation");
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
    goToSurface("decision", "section-engine");
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
    goToSurface("decision", "section-engine");
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
    focusSection("section-suggestions");
  } catch (error) {
    setStatus(`${currentCopy().connectError} ${error.message}`, true);
  }
}

async function askCopilot(questionOverride = null) {
  if (!state.dataset) return;
  const question = (questionOverride || $("question-input").value).trim();
  if (!question) return;
  try {
    const startedAt = performance.now();
    $("question-input").value = question;
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
    state.builderOps.lastRoute = "copilot";
    state.builderOps.lastLatencyMs = Math.round(performance.now() - startedAt);
    setStatus(currentCopy().askDone);
    render();
    goToSurface("decision", "section-copilot");
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
    goToSurface("decision", "section-evidence");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function runSqlQuery(questionOverride = null) {
  const c = currentCopy();
  if (!state.dataset) return;
  const question = (questionOverride || $("sql-question-input").value).trim();
  if (!question) return;
  try {
    const startedAt = performance.now();
    $("sql-question-input").value = question;
    const additionalDatasetIds = (state.datasets || [])
      .map((dataset) => dataset.dataset_id)
      .filter((datasetId) => datasetId !== state.dataset.dataset_id);
    state.sqlQuery = await api("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        question,
        language: state.lang,
        additional_dataset_ids: additionalDatasetIds,
      }),
    });
    state.builderOps.lastRoute = "sql";
    state.builderOps.lastLatencyMs = Math.round(performance.now() - startedAt);
    state.builderOps.queryCount += 1;
    state.builderOps.usedTables = state.sqlQuery.used_tables || [];
    upsertSqlHistory({
      question,
      sql: state.sqlQuery.sql,
      columns: state.sqlQuery.columns,
      row_count: state.sqlQuery.row_count,
      result_preview: state.sqlQuery.result_preview,
      explanation: state.sqlQuery.explanation,
      used_tables: state.sqlQuery.used_tables || [],
      warnings: state.sqlQuery.warnings || [],
    });
    setStatus(c.queryResultTitle);
    await refreshObservability();
    renderSqlQuery();
    renderSqlHistory();
    renderObservability();
    goToSurface("builder", "section-query");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function explainCurrentSql() {
  const c = currentCopy();
  if (!state.sqlQuery) return;
  try {
    const startedAt = performance.now();
    const result = await api("/query/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: state.sqlQuery.question,
        sql: state.sqlQuery.sql,
        language: state.lang,
        columns: state.sqlQuery.columns || [],
        row_count: state.sqlQuery.row_count || 0,
        result_preview: state.sqlQuery.result_preview || [],
      }),
    });
    state.sqlQuery.explanation = result.explanation;
    state.sqlHistory = state.sqlHistory.map((item) =>
      item.question === state.sqlQuery.question && item.sql === state.sqlQuery.sql
        ? { ...item, explanation: result.explanation }
        : item,
    );
    state.builderOps.lastRoute = "sql-explain";
    state.builderOps.lastLatencyMs = Math.round(performance.now() - startedAt);
    setStatus(c.queryExplainDone);
    renderSqlQuery();
    renderSqlHistory();
    renderBuilderOps();
    goToSurface("builder", "section-query");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

function exportCurrentQueryCsv() {
  const c = currentCopy();
  if (!state.sqlQuery?.result_preview?.length || !state.sqlQuery?.columns?.length) return;
  downloadCsv("query-result.csv", state.sqlQuery.result_preview, state.sqlQuery.columns);
  setStatus(c.queryExportDone);
}

function replaySqlHistory(index) {
  const entry = state.sqlHistory[index];
  if (!entry) return;
  $("sql-question-input").value = entry.question;
  state.sqlQuery = { ...entry };
  state.builderOps.usedTables = entry.used_tables || [];
  renderSqlQuery();
  renderBuilderOps();
  goToSurface("builder", "section-query");
}

async function routeQuestion() {
  const c = currentCopy();
  if (!state.dataset) return;
  const question = $("sql-question-input").value.trim();
  if (!question) return;
  const route = classifyQuestion(question);
  try {
    if (route === "sql") {
      await runSqlQuery(question);
      setStatus(c.routeSqlDone);
      return;
    }
    if (route === "prediction") {
      if (!state.training) {
        await trainModel();
      }
      await askCopilot(question);
      setStatus(c.routePredictionDone);
      return;
    }
    if (route === "simulation") {
      if (!state.training) {
        await trainModel();
      }
      await runGuidedSimulation();
      await askCopilot(question);
      setStatus(c.routeSimulationDone);
      return;
    }
    await askCopilot(question);
    setStatus(c.routeCopilotDone);
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function runJoinAssistant() {
  const c = currentCopy();
  if (!state.dataset) return;
  try {
    state.joinAssistant = await api("/join-assistant", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dataset_id: state.dataset.dataset_id, language: state.lang }),
    });
    setStatus(c.joinAssistantTitle);
    await refreshObservability();
    renderJoinAssistant();
    renderObservability();
    goToSurface("builder", "section-builder-studio");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function runSemanticLayer() {
  const c = currentCopy();
  if (!state.dataset) return;
  try {
    state.semanticLayer = await api("/semantic-layer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dataset_id: state.dataset.dataset_id, language: state.lang }),
    });
    setStatus(c.semanticLayerTitle);
    await refreshObservability();
    renderSemanticLayer();
    renderObservability();
    goToSurface("builder", "section-builder-studio");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function runPrepAgent() {
  const c = currentCopy();
  if (!state.dataset) return;
  try {
    state.prepAgent = await api("/prep-agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dataset_id: state.dataset.dataset_id, language: state.lang }),
    });
    setStatus(c.prepAgentTitle);
    await refreshObservability();
    renderPrepAgent();
    renderObservability();
    goToSurface("builder", "section-builder-studio");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function runWorkflowBuilder() {
  const c = currentCopy();
  if (!state.dataset) return;
  try {
    state.workflowBuilder = await api("/workflow-builder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        goal: $("workflow-goal-select").value,
        language: state.lang,
        model_id: state.training?.model_id || null,
      }),
    });
    setStatus(c.workflowBuilderTitle);
    await refreshObservability();
    renderWorkflowBuilder();
    renderObservability();
    goToSurface("builder", "section-builder-studio");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function runQuantOptimizer() {
  const c = currentCopy();
  if (!state.dataset || !state.training) return;
  try {
    state.quantOptimizer = await api("/quant-optimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        model_id: state.training.model_id,
        objective: $("optimizer-objective-select").value,
        language: state.lang,
      }),
    });
    setStatus(c.quantOptimizerTitle);
    await refreshObservability();
    renderQuantOptimizer();
    renderObservability();
    goToSurface("builder", "section-builder-studio");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function refreshObservability() {
  try {
    state.observability = await api("/observability");
  } catch (_error) {
    state.observability = null;
  }
}

async function refreshEvaluationConsole() {
  try {
    state.evaluationConsole = await api("/evaluation-console");
  } catch (_error) {
    state.evaluationConsole = null;
  }
}

async function refreshPlatformOverview() {
  try {
    state.platformOverview = await api("/platform/overview");
  } catch (_error) {
    state.platformOverview = null;
  }
}

async function createWorkspaceUser() {
  const c = currentCopy();
  const name = $("workspace-owner-input").value.trim() || (state.lang === "fr" ? "Builder demo" : "Demo builder");
  try {
    const user = await api("/platform/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, role: "builder" }),
    });
    $("workspace-owner-input").value = user.name;
    await refreshPlatformOverview();
    renderPlatformOverview();
    setStatus(c.userCreated);
    goToSurface("governance", "section-platform");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function createWorkspaceProject() {
  const c = currentCopy();
  const name = $("project-name-input").value.trim() || (state.lang === "fr" ? "Projet demo" : "Demo project");
  const ownerId = state.platformOverview?.users?.[0]?.user_id || null;
  try {
    const project = await api("/platform/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, owner_user_id: ownerId }),
    });
    $("project-name-input").value = project.name;
    await refreshPlatformOverview();
    renderPlatformOverview();
    setStatus(c.projectCreated);
    goToSurface("governance", "section-platform");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function connectAndImportCsv() {
  const c = currentCopy();
  const url = $("connector-url-input").value.trim();
  if (!url) return;
  const name = $("connector-name-input").value.trim() || "CSV source";
  const projectId = state.platformOverview?.projects?.[0]?.project_id || null;
  const createdBy = state.platformOverview?.users?.[0]?.user_id || null;
  try {
    const connector = await api("/platform/connectors", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        connector_type: "csv_url",
        config: { url },
        project_id: projectId,
        created_by: createdBy,
      }),
    });
    state.latestConnectorTest = await api("/platform/connectors/test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ connector_id: connector.connector_id }),
    });
    const dataset = await api("/platform/connectors/import", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ connector_id: connector.connector_id }),
    });
    await refreshPlatformOverview();
    renderPlatformOverview();
    await hydrateDataset(dataset);
    setStatus(c.connectorImported);
    goToSurface("governance", "section-platform");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function exportWorkflowArtifact() {
  const c = currentCopy();
  if (!state.dataset) return;
  try {
    state.latestWorkflowExport = await api("/platform/exports/workflow", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        language: state.lang,
        goal: $("workflow-goal-select").value,
        model_id: state.training?.model_id || null,
        project_id: state.platformOverview?.projects?.[0]?.project_id || null,
        created_by: state.platformOverview?.users?.[0]?.user_id || null,
      }),
    });
    await refreshPlatformOverview();
    renderPlatformOverview();
    setStatus(c.workflowExported);
    goToSurface("governance", "section-platform");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function exportPolicyArtifact() {
  const c = currentCopy();
  if (!state.dataset) return;
  try {
    state.latestPolicyExport = await api("/platform/exports/policy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        language: state.lang,
        model_id: state.training?.model_id || null,
        project_id: state.platformOverview?.projects?.[0]?.project_id || null,
        created_by: state.platformOverview?.users?.[0]?.user_id || null,
      }),
    });
    await refreshPlatformOverview();
    renderPlatformOverview();
    setStatus(c.policyExported);
    goToSurface("governance", "section-platform");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function requestHumanApproval() {
  const c = currentCopy();
  const latestArtifact = state.latestPolicyExport?.artifact || state.latestWorkflowExport?.artifact || state.platformOverview?.exports?.[0];
  const title = $("approval-title-input").value.trim() || (latestArtifact ? `Approve ${latestArtifact.name}` : "Approve builder change");
  const objectType = latestArtifact?.artifact_type || "decision";
  const objectId = latestArtifact?.artifact_id || null;
  const summary = latestArtifact?.summary || (state.lang === "fr" ? "Validation requise avant execution." : "Approval required before execution.");
  try {
    state.latestApproval = await api("/platform/approvals", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        object_type: objectType,
        object_id: objectId,
        summary,
        project_id: state.platformOverview?.projects?.[0]?.project_id || null,
        requested_by: state.platformOverview?.users?.[0]?.user_id || null,
        payload: latestArtifact ? { artifact_id: latestArtifact.artifact_id } : {},
      }),
    });
    await refreshPlatformOverview();
    renderPlatformOverview();
    setStatus(c.approvalRequested);
    goToSurface("governance", "section-platform");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function approveLatestRequest() {
  const c = currentCopy();
  const latestApproval = state.platformOverview?.approvals?.find((item) => item.status === "pending");
  if (!latestApproval) return;
  try {
    state.latestApproval = await api(`/platform/approvals/${latestApproval.approval_id}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        decision: "approved",
        reviewer: state.platformOverview?.users?.[0]?.user_id || null,
        comment: state.lang === "fr" ? "Approuve depuis le studio." : "Approved from the studio.",
      }),
    });
    await refreshPlatformOverview();
    renderPlatformOverview();
    setStatus(c.approvalApproved);
    goToSurface("governance", "section-platform");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function runConstraintSolver() {
  const c = currentCopy();
  if (!state.dataset || !state.training) return;
  try {
    state.constraintSolver = await api("/constraint-solver", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        model_id: state.training.model_id,
        objective: $("optimizer-objective-select").value,
        language: state.lang,
      }),
    });
    setStatus(c.constraintSolverTitle);
    await refreshObservability();
    await refreshEvaluationConsole();
    renderConstraintSolver();
    renderObservability();
    renderEvaluationConsole();
    goToSurface("builder", "section-builder-studio");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function runExperimentDesigner() {
  const c = currentCopy();
  if (!state.dataset) return;
  try {
    state.experimentDesigner = await api("/experiment-designer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        model_id: state.training?.model_id || null,
        language: state.lang,
      }),
    });
    setStatus(c.experimentDesignerTitle);
    await refreshObservability();
    await refreshEvaluationConsole();
    renderExperimentDesigner();
    renderObservability();
    renderEvaluationConsole();
    goToSurface("builder", "section-builder-studio");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function runEvaluationConsole() {
  const c = currentCopy();
  await refreshEvaluationConsole();
  setStatus(c.evaluationConsoleTitle);
  renderEvaluationConsole();
  goToSurface("builder", "section-builder-studio");
}

async function runPolicyEngine() {
  const c = currentCopy();
  if (!state.dataset) return;
  try {
    state.policyEngine = await api("/policy-engine", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        model_id: state.training?.model_id || null,
        language: state.lang,
      }),
    });
    await refreshObservability();
    await refreshEvaluationConsole();
    setStatus(c.policyEngineTitle);
    renderPolicyEngine();
    renderObservability();
    renderEvaluationConsole();
    goToSurface("builder", "section-builder-studio");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function runSemanticKpiRegistry() {
  const c = currentCopy();
  if (!state.dataset) return;
  try {
    state.semanticKpiRegistry = await api("/semantic-kpi-registry", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset.dataset_id,
        language: state.lang,
      }),
    });
    await refreshObservability();
    await refreshEvaluationConsole();
    setStatus(c.semanticKpiRegistryTitle);
    renderSemanticKpiRegistry();
    renderObservability();
    renderEvaluationConsole();
    goToSurface("builder", "section-builder-studio");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

async function runOrchestrationView() {
  const c = currentCopy();
  try {
    state.orchestrationView = await api("/orchestration-view", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: state.dataset?.dataset_id || null,
        language: state.lang,
      }),
    });
    setStatus(c.orchestrationViewTitle);
    renderOrchestrationView();
    goToSurface("builder", "section-builder-studio");
  } catch (error) {
    setStatus(`${c.connectError} ${error.message}`, true);
  }
}

function selectMarketProfile(profile) {
  state.marketProfile = profile;
  if (profile === "revenue" && state.surfaceMode === "governance") {
    state.surfaceMode = "decision";
  }
  render();
}

function selectSurfaceMode(mode) {
  goToSurface(mode);
}

async function applyPlaybook(playbook) {
  const c = currentCopy();
  if (playbook === "pricing") {
    state.marketProfile = "revenue";
    $("workflow-goal-select").value = "pricing_decision";
    $("question-input").value = state.lang === "fr"
      ? "Faut-il augmenter le prix sur les segments premium ?"
      : "Should we increase price on premium segments?";
    setStatus(c.playbookPricingStatus);
    goToSurface("decision", "section-decision-summary");
  } else if (playbook === "growth") {
    state.marketProfile = "revenue";
    $("workflow-goal-select").value = "marketing_optimization";
    $("sql-question-input").value = state.lang === "fr"
      ? "Compare le revenu et le pipeline qualifie par region"
      : "Compare revenue and qualified pipeline by region";
    setStatus(c.playbookGrowthStatus);
    goToSurface("builder", "section-query");
  } else {
    state.marketProfile = "analytics";
    $("approval-title-input").value = state.lang === "fr"
      ? "Validation du workflow executive"
      : "Executive workflow approval";
    setStatus(c.playbookExecStatus);
    goToSurface("governance", "section-platform");
  }
}

function bindEvents() {
  $("persona-revenue").addEventListener("click", () => selectMarketProfile("revenue"));
  $("persona-builder").addEventListener("click", () => selectMarketProfile("builder"));
  $("persona-analytics").addEventListener("click", () => selectMarketProfile("analytics"));
  $("surface-decision").addEventListener("click", () => selectSurfaceMode("decision"));
  $("surface-builder").addEventListener("click", () => selectSurfaceMode("builder"));
  $("surface-governance").addEventListener("click", () => selectSurfaceMode("governance"));
  $("dashboard-tab-decision").addEventListener("click", () => selectSurfaceMode("decision"));
  $("dashboard-tab-builder").addEventListener("click", () => selectSurfaceMode("builder"));
  $("dashboard-tab-governance").addEventListener("click", () => selectSurfaceMode("governance"));
  $("playbook-pricing").addEventListener("click", () => applyPlaybook("pricing"));
  $("playbook-growth").addEventListener("click", () => applyPlaybook("growth"));
  $("playbook-exec").addEventListener("click", () => applyPlaybook("exec"));
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
  $("run-sql-query").addEventListener("click", runSqlQuery);
  $("route-query").addEventListener("click", routeQuestion);
  $("run-join-assistant").addEventListener("click", runJoinAssistant);
  $("run-semantic-layer").addEventListener("click", runSemanticLayer);
  $("run-prep-agent").addEventListener("click", runPrepAgent);
  $("run-workflow-builder").addEventListener("click", runWorkflowBuilder);
  $("run-quant-optimizer").addEventListener("click", runQuantOptimizer);
  $("run-constraint-solver").addEventListener("click", runConstraintSolver);
  $("run-experiment-designer").addEventListener("click", runExperimentDesigner);
  $("run-evaluation-console").addEventListener("click", runEvaluationConsole);
  $("run-policy-engine").addEventListener("click", runPolicyEngine);
  $("run-semantic-kpi-registry").addEventListener("click", runSemanticKpiRegistry);
  $("run-orchestration-view").addEventListener("click", runOrchestrationView);
  $("create-user").addEventListener("click", createWorkspaceUser);
  $("create-project").addEventListener("click", createWorkspaceProject);
  $("connect-import-csv").addEventListener("click", connectAndImportCsv);
  $("export-workflow-artifact").addEventListener("click", exportWorkflowArtifact);
  $("export-policy-artifact").addEventListener("click", exportPolicyArtifact);
  $("request-approval").addEventListener("click", requestHumanApproval);
  $("approve-latest").addEventListener("click", approveLatestRequest);
  $("refresh-platform").addEventListener("click", async () => {
    await refreshPlatformOverview();
    renderPlatformOverview();
  });
  $("explain-sql").addEventListener("click", explainCurrentSql);
  $("export-query-csv").addEventListener("click", exportCurrentQueryCsv);
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
  document.querySelectorAll(".history-replay-btn").forEach((button) => {
    button.onclick = () => replaySqlHistory(Number(button.dataset.historyIndex));
  });
  document.querySelectorAll(".content-tab-btn").forEach((button) => {
    button.onclick = () => {
      state.surfaceSubtabs[state.surfaceMode] = button.dataset.surfaceTab;
      render();
      focusCurrentSubtab();
    };
  });
  document.querySelectorAll('input[type="range"][data-control-type="slider"]').forEach((input) => {
    input.oninput = () => {
      const meta = input.nextElementSibling;
      if (meta) meta.textContent = input.value;
    };
  });
}

function focusInitialRouteTarget() {
  const target = window.location.hash.replace("#", "");
  if (!target) return;
  window.setTimeout(() => focusSection(target), 120);
}

async function init() {
  await refreshHealth();
  await refreshDatasets();
  await refreshObservability();
  await refreshEvaluationConsole();
  await refreshPlatformOverview();
  bindEvents();
  render();
  focusInitialRouteTarget();
}

init();
