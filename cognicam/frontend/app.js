// COGNICAM Frontend Application
// Context-Aware Credit Appraisal Engine

// CONSTANTS
const API_BASE = "https://cognicam.onrender.com";

// Demo Data - Complete realistic responses for all API calls
const DEMO_DATA = {
  ingest: {
    status: "success",
    extracted_data: {
      company_name: "Sunrise Textiles Pvt Ltd",
      gstin: "27AABCS1681D1ZM",
      annual_turnover: 45000000,
      net_profit: 2800000,
      total_debt: 18000000,
      total_assets: 35000000,
      current_ratio: 1.65,
      debt_to_equity: 1.06,
      financial_year: "2023-24"
    },
    gstr_flags: {
      flags: ["ITC Mismatch - 42.6% excess claimed", "Revenue Inflation - 52.2% bank credits excess", "Circular Trading Suspected - 1 overlapping parties"],
      risk_level: "High",
      confidence_score: 0.85,
      explanation: "GST analysis reveals 3 compliance issues: ITC Mismatch - 42.6% excess claimed; Revenue Inflation - 52.2% bank credits excess; Circular Trading Suspected - 1 overlapping parties",
      details: {
        itc_ratio: 1.426,
        revenue_inflation_ratio: 1.522,
        circular_overlap_ratio: 0.2,
        effective_tax_rate: 0.06
      }
    },
    raw_text_preview: "Sunrise Textiles Pvt Ltd - Financial Statement for FY 2023-24...",
    files_processed: ["financial_statement.pdf"]
  }
};


// STATE MANAGEMENT
const state = {
  currentStep: 1,
  files: [],
  extractedData: null,
  gstrFlags: null,
  researchData: null,
  scoringData: null,
  shapData: null,
  fieldNote: "",
  demoMode: false
};

// DOM ELEMENTS
const elements = {};

// INITIALIZATION
document.addEventListener("DOMContentLoaded", function () {
  initializeElements();
  attachEventListeners();
  setInitialState();
  checkBackendHealth();
});

function initializeElements() {
  // Step panels
  elements.stepPanels = document.querySelectorAll(".step-panel");
  elements.stepItems = document.querySelectorAll(".step-item");

  // Upload elements
  elements.uploadZone = document.getElementById("uploadZone");
  elements.fileInput = document.getElementById("fileInput");
  elements.filePills = document.getElementById("filePills");

  // JSON inputs
  elements.gstr2aInput = document.getElementById("gstr2aInput");
  elements.gstr3bInput = document.getElementById("gstr3bInput");
  elements.bankInput = document.getElementById("bankInput");

  // Buttons
  elements.loadSampleBtn = document.getElementById("loadSampleBtn");
  elements.processBtn = document.getElementById("processBtn");
  elements.researchBtn = document.getElementById("researchBtn");
  elements.continueToFieldBtn = document.getElementById("continueToFieldBtn");
  elements.calculateScoreBtn = document.getElementById("calculateScoreBtn");
  elements.continueToReportBtn = document.getElementById("continueToReportBtn");
  elements.generateReportBtn = document.getElementById("generateReportBtn");
  elements.newAppraisalBtn = document.getElementById("newAppraisalBtn");

  // Form inputs
  elements.companyName = document.getElementById("companyName");
  elements.gstinInput = document.getElementById("gstinInput");
  elements.promoterName = document.getElementById("promoterName");
  elements.sectorSelect = document.getElementById("sectorSelect");
  elements.fieldNote = document.getElementById("fieldNote");

  // UI elements
  elements.demoMode = document.getElementById("demoMode");
  elements.demoBanner = document.getElementById("demoBanner");
  elements.charCount = document.getElementById("charCount");
  elements.toastWrap = document.getElementById("toastWrap");
  elements.loadingOverlay = document.getElementById("loadingOverlay");
  elements.loadingText = document.getElementById("loadingText");
}


function attachEventListeners() {
  // Demo mode toggle
  elements.demoMode.addEventListener("change", function () {
    state.demoMode = this.checked;
    elements.demoBanner.style.display = state.demoMode ? "block" : "none";
    showToast(state.demoMode ? "Demo mode activated" : "Demo mode deactivated", "info");
  });

  // File upload
  elements.uploadZone.addEventListener("dragover", handleDragOver);
  elements.uploadZone.addEventListener("dragleave", handleDragLeave);
  elements.uploadZone.addEventListener("drop", handleDrop);
  elements.fileInput.addEventListener("change", handleFileSelect);

  // Buttons
  elements.loadSampleBtn.addEventListener("click", loadSampleData);
  elements.processBtn.addEventListener("click", processDocuments);
  elements.researchBtn.addEventListener("click", runResearch);
  elements.continueToFieldBtn.addEventListener("click", () => goToStep(3));
  elements.calculateScoreBtn.addEventListener("click", calculateScore);
  elements.continueToReportBtn.addEventListener("click", () => goToStep(5));
  elements.generateReportBtn.addEventListener("click", generateReport);
  elements.newAppraisalBtn.addEventListener("click", startNewAppraisal);

  // Field note character counter
  elements.fieldNote.addEventListener("input", updateCharCounter);
}

function setInitialState() {
  goToStep(1);
  updateCharCounter();
}

// STEP NAVIGATION
function goToStep(stepNumber) {
  console.log(`Navigating to step ${stepNumber}`);

  // Update panels
  elements.stepPanels.forEach(panel => {
    panel.classList.remove("active");
  });
  const stepElement = document.getElementById(`step-${stepNumber}`);
  if (stepElement) {
    stepElement.classList.add("active");
  }

  // Update progress bar
  elements.stepItems.forEach((item, index) => {
    const step = index + 1;
    item.classList.remove("active", "done");

    if (step === stepNumber) {
      item.classList.add("active");
    } else if (step < stepNumber) {
      item.classList.add("done");
    }
  });

  state.currentStep = stepNumber;

  // Smooth scroll to top
  window.scrollTo({ top: 0, behavior: "smooth" });
}


// API FUNCTIONS
async function processDocuments() {
  console.log("Processing documents...");
  showLoading("Processing documents...");

  try {
    if (state.demoMode) {
      console.log("Using demo mode for document processing");
      await new Promise(resolve => setTimeout(resolve, 1500));

      const response = DEMO_DATA.ingest;
      state.extractedData = response.extracted_data;
      state.gstrFlags = response.gstr_flags;

      hideLoading();
      showToast("Documents processed successfully (Demo)", "success");
      goToStep(2);
      return;
    }

    // Real API call would go here
    showToast("Backend API not implemented in demo", "info");
    hideLoading();

  } catch (error) {
    console.error("Document processing error:", error);
    hideLoading();
    showToast("Failed to process documents: " + error.message, "error");
  }
}

async function runResearch() {
  console.log("Running company research...");

  const companyName = elements.companyName.value.trim();
  if (!companyName) {
    showToast("Please enter company name", "error");
    return;
  }

  // Show loading state
  const researchLoading = document.getElementById("researchLoading");
  const researchResults = document.getElementById("researchResults");

  researchLoading.style.display = "block";
  researchResults.style.display = "none";

  try {
    if (state.demoMode) {
      console.log("Using demo mode for research");

      // Simulate step-by-step loading
      const steps = researchLoading.querySelectorAll(".research-step");

      for (let i = 0; i < steps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 800));
        steps[i].classList.add("done");
      }

      await new Promise(resolve => setTimeout(resolve, 500));

      researchLoading.style.display = "none";
      renderResearchResults();
      researchResults.style.display = "block";

      showToast("Research completed successfully (Demo)", "success");
    }

  } catch (error) {
    console.error("Research error:", error);
    researchLoading.style.display = "none";
    showToast("Demo mode: Using cached intelligence dataset", "info");
  }
}


function renderResearchResults() {
  // Mock MCA data
  const mcaHtml = `
    <div class="mca-info">
      <p><strong>Company:</strong> Sunrise Textiles Pvt Ltd</p>
      <p><strong>CIN:</strong> <span style="font-family: monospace;">2745678PLPTC1234</span></p>
      <p><strong>Status:</strong> <span class="chip" style="background: var(--emerald);">Active</span></p>
      <p><strong>Incorporation:</strong> 2015-06-15</p>
    </div>
  `;
  document.getElementById("mcaResults").innerHTML = mcaHtml;

  // Mock litigation data
  const litigationHtml = `
    <p style="color: var(--amber);">⚠ 1 Pending Case</p>
    <p><strong>CS/2023/456</strong></p>
    <p><em>Delhi High Court</em></p>
    <p>Loan Recovery</p>
  `;
  document.getElementById("litigationResults").innerHTML = litigationHtml;

  // Mock news data
  const newsHtml = `
    <div class="sentiment-stats">
      <span class="chip" style="background: var(--emerald);">2 Positive</span>
      <span class="chip" style="background: var(--danger);">1 Negative</span>
      <span class="chip" style="background: var(--amber);">2 Neutral</span>
    </div>
    <div class="news-articles">
      <p>🟢 Sunrise Textiles Reports Strong Q3 Growth</p>
      <p>🔴 NPA Concerns: Loan Account Under Monitoring</p>
    </div>
  `;
  document.getElementById("newsResults").innerHTML = newsHtml;
}

async function calculateScore() {
  console.log("Calculating credit score...");

  showLoading("Analyzing field notes...");
  setTimeout(() => showLoading("Computing Five Cs..."), 1000);
  setTimeout(() => showLoading("Running SHAP analysis..."), 2000);

  try {
    if (state.demoMode) {
      console.log("Using demo mode for scoring");
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Mock scoring data
      const scores = { character: 65, capacity: 72, capital: 80, collateral: 60, conditions: 55 };
      const rationales = {
        character: "1 active litigation cases (-15)",
        capacity: "Adequate current ratio; Positive net profit (+10)",
        capital: "Moderate debt-to-equity ratio; Strong asset base (+10)",
        collateral: "Standard collateral assessment",
        conditions: "Standard conditions assessment"
      };

      hideLoading();
      renderScoringDashboard(scores, rationales);
      showToast("Credit scoring completed (Demo)", "success");
    }

  } catch (error) {
    console.error("Scoring error:", error);
    hideLoading();
    showToast("Failed to calculate score: " + error.message, "error");
  }
}


function renderScoringDashboard(scores, rationales) {
  // Render score rings
  const params = ["character", "capacity", "capital", "collateral", "conditions"];

  params.forEach((param, index) => {
    const score = scores[param];
    const rationale = rationales[param];

    // Update score text with animation
    const scoreElement = document.getElementById(`${param}Score`);
    animateCounter(scoreElement, score, 1500);

    // Update ring fill
    const ringElement = document.getElementById(`${param}Ring`);
    const circumference = 2 * Math.PI * 45;
    const offset = circumference - (score / 100) * circumference;

    setTimeout(() => {
      ringElement.style.strokeDashoffset = offset;

      if (score >= 75) {
        ringElement.style.stroke = "var(--emerald)";
      } else if (score >= 50) {
        ringElement.style.stroke = "var(--amber)";
      } else {
        ringElement.style.stroke = "var(--danger)";
      }
    }, index * 150);

    // Update grade
    const gradeElement = document.getElementById(`${param}Grade`);
    const grade = getGrade(score);
    gradeElement.textContent = grade.letter;
    gradeElement.className = `ring-grade grade-${grade.letter.toLowerCase()}`;

    // Update rationale
    const rationaleElement = document.getElementById(`${param}Rationale`);
    rationaleElement.textContent = rationale.substring(0, 60) + "...";
  });

  // Render recommendation
  renderRecommendation();

  // Render GSTR flags
  renderGstrFlags();
}

function animateCounter(element, targetValue, duration) {
  const startValue = 0;
  const increment = targetValue / (duration / 20);
  let currentValue = startValue;

  const timer = setInterval(() => {
    currentValue += increment;
    if (currentValue >= targetValue) {
      currentValue = targetValue;
      clearInterval(timer);
    }
    element.textContent = Math.round(currentValue);
  }, 20);
}

function getGrade(score) {
  if (score >= 75) return { letter: "A", text: "Excellent" };
  if (score >= 50) return { letter: "B", text: "Satisfactory" };
  return { letter: "C", text: "Poor" };
}

function renderRecommendation() {
  const finalScore = 66.4;
  const decision = "CONDITIONAL APPROVE";
  const creditLimit = 0.9;
  const interestRate = 11.0;
  const tenor = "24 months";
  const confidence = 0.664;

  // Update amount
  elements.recAmount.textContent = `₹${creditLimit.toFixed(2)} Cr`;
  elements.recTerms.textContent = `@ ${interestRate}% for ${tenor}`;

  // Update confidence
  elements.confidenceValue.textContent = `${Math.round(confidence * 100)}%`;

  // Update risk grade
  elements.riskGrade.textContent = "B";
  elements.riskGrade.className = "risk-grade grade-b";
}

function renderGstrFlags() {
  const flagsHtml = `
    <span class="flag-chip" style="background: var(--amber);">⚠ ITC Mismatch</span>
    <span class="flag-chip" style="background: var(--amber);">⚠ Revenue Inflation</span>
    <span class="flag-chip" style="background: var(--danger);">⚠ Circular Trading</span>
  `;
  elements.flagsContainer.innerHTML = flagsHtml;
}

async function generateReport() {
  console.log("Generating CAM report...");
  showLoading("Generating CAM report...");

  try {
    if (state.demoMode) {
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Create a mock download
      const blob = new Blob(["Mock CAM Report Content"], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "CAM_Sunrise_Textiles.docx";
      a.click();

      URL.revokeObjectURL(url);

      hideLoading();
      showToast("CAM report downloaded (Demo)", "success");
    }

  } catch (error) {
    console.error("Report generation error:", error);
    hideLoading();
    showToast("Failed to generate report: " + error.message, "error");
  }
}

function startNewAppraisal() {
  console.log("Starting new appraisal...");

  // Reset state
  state.currentStep = 1;
  state.files = [];
  state.extractedData = null;
  state.gstrFlags = null;
  state.researchData = null;
  state.scoringData = null;
  state.shapData = null;
  state.fieldNote = "";

  // Reset UI
  elements.filePills.innerHTML = "";
  elements.gstr2aInput.value = "";
  elements.gstr3bInput.value = "";
  elements.bankInput.value = "";
  elements.companyName.value = "";
  elements.gstinInput.value = "";
  elements.promoterName.value = "";
  elements.sectorSelect.value = "general";
  elements.fieldNote.value = "";

  goToStep(1);
  showToast("Ready for new appraisal", "info");
}

// UTILITY FUNCTIONS
function updateCharCounter() {
  const length = elements.fieldNote.value.length;
  elements.charCount.textContent = length;

  if (length > 500) {
    elements.fieldNote.value = elements.fieldNote.value.substring(0, 500);
    elements.charCount.textContent = 500;
  }
}

function showToast(message, type = "info") {
  console.log(`Toast: ${message} (${type})`);

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;

  elements.toastWrap.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 4000);
}

function showLoading(text = "Loading...") {
  elements.loadingText.textContent = text;
  elements.loadingOverlay.style.display = "flex";
}

function hideLoading() {
  elements.loadingOverlay.style.display = "none";
}

async function checkBackendHealth() {
  try {
    const response = await fetch("http://localhost:8000/health");
    if (response.ok) {
      console.log("Backend is online");
    } else {
      showToast("Backend appears to be offline - enable Demo Mode to continue", "error");
    }
  } catch (error) {
    console.log("Backend health check failed:", error);
    showToast("Backend appears to be offline - enable Demo Mode to continue", "error");
  }
}

