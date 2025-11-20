function openModal(id, date, requestor, office, unit, description, status, personnel, materials, reports, labor, materials_needed, others_needed, cancelReason, reqSelectedIndicatorId) {
  document.getElementById("modal-date").textContent = date;
  document.getElementById("modal-requestor").textContent = requestor;
  document.getElementById("modal-office").textContent = office;
  document.getElementById("modal-unit").textContent = unit;
  document.getElementById("modal-description").textContent = description;
  document.getElementById("modal-personnel").textContent = personnel || "Unassigned";
  document.getElementById("modal-materials").textContent = materials || "No materials assigned";
  document.getElementById("modal-reports").innerHTML = reports || "No reports submitted";

  // ===== Category Logic =====
  labor = labor === "True" || labor === true || labor === "1";
  materials_needed = materials_needed === "True" || materials_needed === true || materials_needed === "1";
  others_needed = others_needed === "True" || others_needed === true || others_needed === "1";

  const categories = [];
  if (labor) categories.push("Labor");
  if (materials_needed) categories.push("Materials");
  if (others_needed) categories.push("Others");

  document.getElementById("modal-category").textContent = categories.length ? categories.join(", ") : "None";

  // ===== Status Badge =====
  const statusElement = document.getElementById("modal-status");
  statusElement.textContent = status;
  statusElement.className = 'status-badge';
  switch(status) {
    case "Pending": statusElement.classList.add("pending"); break;
    case "Approved": statusElement.classList.add("approved"); break;
    case "In Progress": statusElement.classList.add("in-progress"); break;
    case "Done for Review": statusElement.classList.add("review"); break;
    case "Completed": statusElement.classList.add("completed"); break;
    case "Cancelled": statusElement.classList.add("cancelled"); break;
    case "Emergency": statusElement.classList.add("emergency"); break;
  }

  const cancelReasonEl = document.getElementById("modal-cancel-reason");
  if (status === "Cancelled" && cancelReason && cancelReason.trim() !== "" && cancelReason !== "None") {
      cancelReasonEl.innerHTML = `<strong>Reason for Cancellation:</strong><br>${cancelReason}`;
      cancelReasonEl.style.display = "block";
  } else {
      cancelReasonEl.style.display = "none";
  }

  // ===== Approve Form Logic =====
  const approveForm = document.getElementById("approveForm");
  if (approveForm) {
    approveForm.action = `/gso_requests/approve/${id}/`;
    approveForm.style.display = (status === "Pending" && personnel && personnel.trim() !== "") ? "block" : "none";
  }

  // ===== Success Indicator Form Logic =====
  const indicatorForm = document.getElementById("indicatorForm");
  const indicatorSelect = document.querySelector("#indicatorForm select[name='selected_indicator']");

  if (indicatorForm && indicatorSelect) {
      indicatorForm.action = `/gso_requests/request/${id}/update_indicator/`;

      // Clear existing options
      indicatorSelect.innerHTML = '<option value="">-- Select Success Indicator --</option>';

      // Populate indicators from Django
      if (typeof indicators !== 'undefined') {
          indicators.forEach(si => {
              const option = document.createElement("option");
              option.value = si.id;
              option.textContent = `${si.code} - ${si.description}`;

              if (reqSelectedIndicatorId && parseInt(reqSelectedIndicatorId) === si.id) {
                  option.selected = true;
              }

              indicatorSelect.appendChild(option);
          });
      }

      // ===== DISABLE SUCCESS INDICATOR WHEN STATUS = COMPLETED =====
      const saveBtn = indicatorForm.querySelector("button[type='submit']");

      if (status === "Completed") {
          indicatorSelect.disabled = true;
          if (saveBtn) saveBtn.disabled = true;
          indicatorForm.style.opacity = "0.6";
          indicatorForm.style.pointerEvents = "none";
      } else {
          indicatorSelect.disabled = false;
          if (saveBtn) saveBtn.disabled = false;
          indicatorForm.style.opacity = "1";
          indicatorForm.style.pointerEvents = "auto";
      }
  }

  new bootstrap.Modal(document.getElementById("requestModal")).show();
}
