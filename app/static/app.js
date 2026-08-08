let currentSessionId = 'session-' + Date.now();
let selectedCandidate = null;
let candidatesList = [];

// Helper to switch screen views in Single Page Application (SPA)
function showView(viewId) {
  const views = ['landingView', 'selectionView', 'chatView', 'feedbackView'];
  views.forEach(v => {
    const el = document.getElementById(v);
    if (el) {
      if (v === viewId) {
        if (v === 'chatView') {
          el.style.display = 'flex';
        } else if (v === 'selectionView') {
          el.style.display = 'flex';
        } else if (v === 'landingView') {
          el.style.display = 'block';
        } else {
          el.style.display = 'block';
        }
      } else {
        el.style.display = 'none';
      }
    }
  });

  // Handle header and sidebar visibility on landing page
  const header = document.querySelector('header');
  const sidebar = document.querySelector('aside');
  const mainPanel = document.getElementById('mainContentPanel');
  
  if (viewId === 'landingView') {
    if (header) header.classList.add('hidden');
    if (sidebar) {
      sidebar.classList.add('hidden');
      sidebar.classList.remove('lg:flex');
    }
    if (mainPanel) {
      mainPanel.classList.remove('lg:ml-[260px]');
    }
  } else {
    if (header) header.classList.remove('hidden');
    if (sidebar) {
      sidebar.classList.remove('hidden');
      sidebar.classList.add('lg:flex');
    }
    if (mainPanel) {
      mainPanel.classList.add('lg:ml-[260px]');
    }
  }

  // Update navigation styles
  const navChat = document.getElementById('navLiveChat');
  const navReport = document.getElementById('navFeedback');
  if (navChat) {
    if (viewId === 'chatView') {
      navChat.classList.remove('text-on-surface-variant');
      navChat.classList.add('text-on-surface', 'font-bold', 'border-b-2', 'border-primary');
    } else {
      navChat.classList.add('text-on-surface-variant');
      navChat.classList.remove('text-on-surface', 'font-bold', 'border-b-2', 'border-primary');
    }
  }
  if (navReport) {
    if (viewId === 'feedbackView') {
      navReport.classList.remove('text-on-surface-variant');
      navReport.classList.add('text-on-surface', 'font-bold', 'border-b-2', 'border-primary');
    } else {
      navReport.classList.add('text-on-surface-variant');
      navReport.classList.remove('text-on-surface', 'font-bold', 'border-b-2', 'border-primary');
    }
  }
}

// Load default candidates from static folder
async function loadCandidates() {
  try {
    const res = await fetch('/static/candidate_profiles.json');
    if (res.ok) {
      const data = await res.json();
      candidatesList = data.candidates || [];
    }
  } catch (e) {
    console.warn('candidate_profiles.json fetch failed, using memory fallback');
    candidatesList = [
      {
        member: { id: "CAND-001", name: 'Sarah Johnson', jobRole: 'Senior Data Engineer', yearsExperience: 9, education: 'MS Computer Science' },
        missions: [{ day: 7, title: "Embeddings Explained", passed: true }],
        signals: { missionsCompleted: 30 }
      },
      {
        member: { id: "CAND-002", name: 'Alex Turner', jobRole: 'Backend Software Engineer', yearsExperience: 5, education: 'B.Tech Computer Science' },
        missions: [{ day: 10, title: "Retrieval & Matching Engine", passed: true }],
        signals: { missionsCompleted: 22 }
      },
      {
        member: { id: "CAND-003", name: 'Emily Chen', jobRole: 'AI Engineer', yearsExperience: 6, education: 'MS Artificial Intelligence' },
        missions: [{ day: 22, title: "Multi-Agent Orchestration", passed: true }],
        signals: { missionsCompleted: 28 }
      }
    ];
  }
  renderCandidateSelector();
}

function renderCandidateSelector() {
  const container = document.getElementById('candidateSelector');
  if (!container) return;
  container.innerHTML = '';

  candidatesList.forEach((c, idx) => {
    const m = c.member || c;
    const missions = c.missions || [];
    const passedMissions = missions.filter(x => x.passed);
    const missionsCount = passedMissions.length;
    const completedCount = c.signals ? (c.signals.missionsCompleted || missionsCount) : missionsCount;
    const curriculumPct = Math.round((completedCount / 31) * 100);

    // Calculate strong and weak topics based on passed/attempts signals
    const strongTopics = passedMissions
      .filter(x => (x.attempts || 1) <= 2)
      .slice(0, 3)
      .map(x => x.title);
    if (strongTopics.length === 0) {
      strongTopics.push("Core Coding", "Software Fundamentals");
    }

    const weakTopics = missions
      .filter(x => x.skipped || (x.attempts || 0) > 3)
      .slice(0, 2)
      .map(x => x.title);
    if (weakTopics.length === 0) {
      weakTopics.push("Edge-case Optimization", "Advanced Scaling");
    }

    const card = document.createElement('div');
    card.className = `glass-panel p-6 rounded-2xl border border-white/10 relative overflow-hidden flex flex-col justify-between glass-panel-hover text-left shadow-lg`;

    const initials = m.name.split(' ').map(n => n[0]).join('');

    card.innerHTML = `
      <div class="flex justify-between items-start mb-4">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-full bg-gradient-to-tr from-primary to-surface-tint flex items-center justify-center text-background font-extrabold text-sm">
            ${initials}
          </div>
          <div>
            <h3 class="font-bold text-on-surface leading-tight text-base">${m.name}</h3>
            <p class="text-xs text-primary font-medium">${m.jobRole || 'Software Engineer'}</p>
          </div>
        </div>
      </div>
      
      <!-- Cohort Progress Bar Widget -->
      <div class="mb-4 bg-white/5 border border-white/5 p-3 rounded-xl">
        <div class="flex justify-between items-center text-[10px] text-outline uppercase tracking-wider font-extrabold mb-1.5">
          <span>Cohort Progress</span>
          <span class="text-primary font-black">${curriculumPct}%</span>
        </div>
        <div class="w-full h-1.5 bg-surface-container rounded-full overflow-hidden border border-white/5">
          <div class="h-full rounded-full bg-gradient-to-r from-primary to-primary-container" style="width: ${curriculumPct}%"></div>
        </div>
      </div>

      <div class="space-y-3 flex-1 text-sm mb-6">
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-outline text-lg">work_history</span>
          <div>
            <p class="text-[10px] text-outline uppercase tracking-wider font-semibold">Experience</p>
            <p class="text-xs text-on-surface font-medium">${m.yearsExperience || 2} Years</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-outline text-lg">school</span>
          <div>
            <p class="text-[10px] text-outline uppercase tracking-wider font-semibold">Education</p>
            <p class="text-xs text-on-surface font-medium">${m.education || 'CS / Engineering'}</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <span class="material-symbols-outlined text-outline text-lg">task_alt</span>
          <div>
            <p class="text-[10px] text-outline uppercase tracking-wider font-semibold">Completed Missions</p>
            <p class="text-xs text-on-surface font-medium">${completedCount} Assessments</p>
          </div>
        </div>
        
        <div class="border-t border-white/5 pt-3">
          <p class="text-[10px] text-emerald-400 uppercase tracking-wider font-semibold mb-1">Strong Topics</p>
          <div class="flex flex-wrap gap-1">
            ${strongTopics.map(t => `<span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/10 px-2 py-0.5 rounded text-[10px]">${t}</span>`).join('')}
          </div>
        </div>
        
        <div class="border-t border-white/5 pt-3">
          <p class="text-[10px] text-orange-400 uppercase tracking-wider font-semibold mb-1">Weak Topics</p>
          <div class="flex flex-wrap gap-1">
            ${weakTopics.map(t => `<span class="bg-orange-500/10 text-orange-400 border border-orange-500/10 px-2 py-0.5 rounded text-[10px]">${t}</span>`).join('')}
          </div>
        </div>
      </div>
      
      <button class="w-full btn-primary-gradient py-2.5 rounded-full text-white font-semibold text-xs shadow-lg active:scale-95 transition-all flex items-center justify-center gap-2" onclick="startNewInterview(${idx})">
        <span class="material-symbols-outlined text-sm">play_circle</span>
        Start Interview
      </button>
    `;
    container.appendChild(card);
  });
}

async function startNewInterview(candidateIdx) {
  const candidate = candidatesList[candidateIdx];
  if (!candidate) return;
  selectedCandidate = candidate;
  
  currentSessionId = 'session-' + Date.now();
  
  const m = candidate.member || candidate;
  document.getElementById('activeCandidateName').innerText = m.name;
  document.getElementById('activeCandidateRole').innerText = m.jobRole || 'Senior Engineer';

  const history = document.getElementById('chatHistory');
  history.innerHTML = '';
  appendAgentMessage('Initializing adaptive interview plan and loading curriculum embeddings...', false);

  showView('chatView');

  const payload = {
    sessionId: currentSessionId,
    candidate: candidate
  };

  try {
    const res = await fetch('/api/interview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    history.innerHTML = '';
    appendAgentMessage(data.reply, false);
    updateMetrics();
  } catch (e) {
    console.error(e);
    history.innerHTML = '';
    appendAgentMessage('Error starting interview session. Please try again.', false);
  }
}

async function sendAnswer(textOverride = null) {
  const input = document.getElementById('answerInput');
  const answerText = textOverride || input.value.trim();
  if (!answerText) return;

  if (!textOverride) input.value = '';
  appendCandidateMessage(answerText);

  const payload = {
    sessionId: currentSessionId,
    message: answerText
  };

  // Append typing indicator
  const typingId = appendTypingIndicator();

  try {
    const res = await fetch('/api/interview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    removeMessage(typingId);
    
    appendAgentMessage(data.reply, false);

    if (data.done && data.feedback) {
      showFeedbackReport(data.feedback);
    } else {
      updateMetrics();
    }
  } catch (e) {
    removeMessage(typingId);
    appendAgentMessage('I had an issue communicating with the model. Let\'s continue our session.', false);
  }
}

async function terminateSessionEarly() {
  const typingId = appendTypingIndicator();
  try {
    const res = await fetch('/interview/end', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: currentSessionId })
    });
    removeMessage(typingId);
    if (res.ok) {
      const data = await res.json();
      showFeedbackReport(data.feedback);
    } else {
      alert('Failed to terminate session early.');
    }
  } catch (e) {
    removeMessage(typingId);
    alert('Network error terminating interview.');
  }
}

async function updateMetrics() {
  try {
    const res = await fetch(`/interview/status/${currentSessionId}`);
    if (res.ok) {
      const data = await res.json();
      
      // Progress numbers
      document.getElementById('qAsked').innerText = data.questions_asked;
      document.getElementById('qBudget').innerText = ` / ${data.question_budget}`;
      
      // Progress Bar width
      const pct = Math.min(100, Math.max(0, (data.questions_asked / data.question_budget) * 100));
      document.getElementById('progressFill').style.width = `${pct}%`;
      document.getElementById('qPercent').innerText = `${Math.round(pct)}% Completed`;
      
      // Days covered
      document.getElementById('daysCovered').innerText = `${data.days_covered} days`;
      
      // Difficulty pill status styling
      const pill = document.getElementById('diffBadge');
      pill.innerText = data.current_difficulty;
      pill.className = `text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider bg-surface-container ${getDifficultyClass(data.current_difficulty)}`;
      
      // Average score gauge
      document.getElementById('avgScore').innerText = `${Math.round(data.average_score * 100)}%`;
      
      // Update SVG Circular dash offset
      const circle = document.getElementById('scoreCircle');
      if (circle) {
        const radius = 40;
        const circumference = 2 * Math.PI * radius; // 251.2
        const offset = circumference - (data.average_score * circumference);
        circle.style.strokeDashoffset = offset;
      }

      // Populate topics covered matrix checklist
      populateTopicsMatrix(data.topics_covered, data.current_topic);
    }
  } catch (e) {
    console.error('Error fetching metrics:', e);
  }
}

function getDifficultyClass(diff) {
  switch (diff) {
    case 'very_easy': return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
    case 'easy': return 'bg-teal-500/10 text-teal-400 border border-teal-500/20';
    case 'medium': return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
    case 'medium_plus': return 'bg-orange-500/10 text-orange-400 border border-orange-500/20';
    case 'hard': return 'bg-rose-500/10 text-rose-400 border border-rose-500/20';
    default: return 'bg-surface-container text-on-surface-variant';
  }
}

function populateTopicsMatrix(coveredTopics, currentTopic) {
  const container = document.getElementById('topicsList');
  if (!container) return;
  container.innerHTML = '';

  // Core curriculum default tracks if empty
  const defaultTracks = ['Environment Setup', 'Embeddings & Vector Database', 'Agentic Workflows', 'Model Context Protocol', 'Production Security'];
  const allTracks = coveredTopics && coveredTopics.length > 0 ? coveredTopics : defaultTracks;

  allTracks.forEach(topic => {
    const isCurrent = topic === currentTopic;
    const li = document.createElement('li');
    li.className = `flex items-center gap-3 ${isCurrent ? 'bg-surface-variant/30 p-2 rounded-lg border border-white/5 -mx-2' : ''}`;
    
    li.innerHTML = `
      <div class="w-5 h-5 rounded ${isCurrent ? 'border border-on-surface-variant/50 flex items-center justify-center' : 'bg-primary/20 border border-primary/50 flex items-center justify-center'}">
        ${isCurrent ? '<div class="w-2 h-2 rounded-full bg-tertiary animate-pulse"></div>' : '<span class="material-symbols-outlined text-primary text-[14px]" style="font-variation-settings: \'FILL\' 1;">check</span>'}
      </div>
      <span class="font-body-md text-sm ${!isCurrent ? 'line-through opacity-60' : 'font-medium'}">${topic}</span>
    `;
    container.appendChild(li);
  });
}

function appendAgentMessage(text, isTyping = false) {
  const id = 'msg-' + Date.now();
  const history = document.getElementById('chatHistory');
  const div = document.createElement('div');
  div.id = id;
  div.className = 'flex items-start gap-3 w-[85%]';
  
  // Format newline characters to paragraphs
  const formattedText = text.replace(/\n\n/g, '</p><p class="mt-2">').replace(/\n/g, '<br>');

  div.innerHTML = `
    <div class="w-8 h-8 rounded-full bg-primary-container/20 flex items-center justify-center border border-primary/30 flex-shrink-0 mt-1">
      <span class="material-symbols-outlined text-primary text-sm">smart_toy</span>
    </div>
    <div class="bg-surface-variant/80 border border-white/10 p-4 rounded-2xl rounded-tl-sm shadow-sm backdrop-blur-md">
      <p class="text-sm text-on-surface leading-relaxed">${formattedText}</p>
    </div>
  `;
  history.appendChild(div);
  history.scrollTop = history.scrollHeight;
  return id;
}

function appendCandidateMessage(text) {
  const history = document.getElementById('chatHistory');
  const div = document.createElement('div');
  div.className = 'flex items-start gap-3 w-[85%] self-end flex-row-reverse';
  
  div.innerHTML = `
    <div class="w-8 h-8 rounded-full bg-secondary-container/30 flex items-center justify-center border border-secondary/30 flex-shrink-0 mt-1">
      <span class="material-symbols-outlined text-secondary text-sm">person</span>
    </div>
    <div class="bg-primary-container/10 border border-primary/20 p-4 rounded-2xl rounded-tr-sm shadow-sm backdrop-blur-md">
      <p class="text-sm text-on-surface leading-relaxed">${text}</p>
    </div>
  `;
  history.appendChild(div);
  history.scrollTop = history.scrollHeight;
}

function appendTypingIndicator() {
  const id = 'typing-' + Date.now();
  const history = document.getElementById('chatHistory');
  const div = document.createElement('div');
  div.id = id;
  div.className = 'flex items-start gap-3 w-[85%]';
  
  div.innerHTML = `
    <div class="w-8 h-8 rounded-full bg-primary-container/20 flex items-center justify-center border border-primary/30 flex-shrink-0 mt-1">
      <span class="material-symbols-outlined text-primary text-sm">smart_toy</span>
    </div>
    <div class="bg-surface-container-high/50 border border-white/5 p-4 rounded-2xl rounded-tl-sm shadow-sm backdrop-blur-md flex items-center gap-1">
      <div class="w-2 h-2 rounded-full bg-on-surface-variant animate-pulse"></div>
      <div class="w-2 h-2 rounded-full bg-on-surface-variant animate-pulse" style="animation-delay: 0.2s"></div>
      <div class="w-2 h-2 rounded-full bg-on-surface-variant animate-pulse" style="animation-delay: 0.4s"></div>
    </div>
  `;
  history.appendChild(div);
  history.scrollTop = history.scrollHeight;
  return id;
}

function removeMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function showFeedbackReport(fb) {
  const m = selectedCandidate.member || selectedCandidate;
  
  document.getElementById('reportCandidateName').innerText = m.name;
  
  const recBadge = document.getElementById('recommendationBadge');
  const rec = (fb.hiring_recommendation || 'hire').toUpperCase().replace('_', ' ');
  recBadge.innerText = rec;

  // Custom coloring for recommendation badge
  if (rec.includes('STRONG HIRE')) {
    recBadge.className = 'px-3 py-1 rounded-full text-xs font-bold tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
  } else if (rec.includes('WEAK HIRE')) {
    recBadge.className = 'px-3 py-1 rounded-full text-xs font-bold tracking-wider bg-amber-500/10 text-amber-400 border border-amber-500/20';
  } else if (rec.includes('NO HIRE')) {
    recBadge.className = 'px-3 py-1 rounded-full text-xs font-bold tracking-wider bg-rose-500/10 text-rose-400 border border-rose-500/20';
  } else {
    recBadge.className = 'px-3 py-1 rounded-full text-xs font-bold tracking-wider bg-primary/10 text-primary border border-primary/20';
  }

  // Display score
  const finalScore = fb.overall_score || 8.0;
  document.getElementById('reportScore').innerText = finalScore;

  // Calculate and animate circular score ring
  const scorePercentVal = Math.round((finalScore / 10.0) * 100);
  const scorePercentEl = document.getElementById('reportScorePercent');
  if (scorePercentEl) {
    scorePercentEl.innerText = `${scorePercentVal}%`;
  }
  
  const reportCircle = document.getElementById('reportScoreCircle');
  if (reportCircle) {
    const radius = reportCircle.r.baseVal.value;
    const circumference = 2 * Math.PI * radius; // 251.2
    const offset = circumference - (scorePercentVal / 100) * circumference;
    reportCircle.style.strokeDasharray = `${circumference}`;
    reportCircle.style.strokeDashoffset = `${offset}`;
  }

  // Executive summary
  document.getElementById('fbSummary').innerText = fb.executive_summary || 'Evaluation report compiled successfully.';
  
  // Strengths list
  const strengthsList = document.getElementById('fbStrengths');
  strengthsList.innerHTML = (fb.strengths || ["Detailed domain explanations", "Clear analytical structure"]).map(s => `
    <li class="flex items-start gap-2">
      <span class="material-symbols-outlined text-emerald-400 text-base mt-0.5">check_circle</span>
      <span>${s}</span>
    </li>
  `).join('');

  // Gaps list
  const gapsList = document.getElementById('fbGaps');
  gapsList.innerHTML = (fb.areas_for_growth || ["Review error tracking edges", "Provide more concrete implementation steps"]).map(g => `
    <li class="flex items-start gap-2">
      <span class="material-symbols-outlined text-tertiary-container text-base mt-0.5">flag</span>
      <span>${g}</span>
    </li>
  `).join('');

  // Actions list
  const nextList = document.getElementById('fbNext');
  nextList.innerHTML = (fb.actionable_recommendations || ["Review operational logging practices", "Deepen testing on edge routing cases"]).map(n => `
    <li class="flex items-center gap-2">
      <span class="material-symbols-outlined text-primary text-base">arrow_right</span>
      <span>${n}</span>
    </li>
  `).join('');

  // Dotted Topic-wise Breakdown
  const breakdownContainer = document.getElementById('fbTopicBreakdown');
  if (breakdownContainer) {
    if (fb.topic_breakdown && fb.topic_breakdown.length > 0) {
      breakdownContainer.innerHTML = fb.topic_breakdown.map(tb => {
        const pct = Math.round(tb.score * 10);
        const maxLen = 35;
        const dotsCount = Math.max(3, maxLen - tb.topic.length);
        const dots = '.'.repeat(dotsCount);
        return `<div class="flex justify-between w-full">
          <span>${tb.topic} ${dots}</span>
          <span class="font-bold">${pct}%</span>
        </div>`;
      }).join('');
    } else {
      breakdownContainer.innerHTML = '<div class="text-xs text-on-surface-variant">No topic data available</div>';
    }
  }

  // Reasoning Block
  const reasoningTextEl = document.getElementById('reportReasoningText');
  if (reasoningTextEl) {
    const reasoning = fb.interview_statistics ? fb.interview_statistics.hiring_reasoning : null;
    const reasoningStr = Array.isArray(reasoning) ? reasoning.join(' ') : (reasoning || 'No reasoning details compiled.');
    reasoningTextEl.innerText = reasoningStr;
  }

  // Interview Statistics Grid
  if (fb.interview_statistics) {
    const stats = fb.interview_statistics;
    document.getElementById('statQuestions').innerText = stats.questions_asked !== undefined ? stats.questions_asked : '0';
    document.getElementById('statFollowups').innerText = stats.followup_questions !== undefined ? stats.followup_questions : '0';
    document.getElementById('statAvgScore').innerText = `${Math.round(stats.avg_score_pct || 0)}%`;
    document.getElementById('statHighest').innerText = `${Math.round(stats.highest_score || 0)}%`;
    document.getElementById('statLowest').innerText = `${Math.round(stats.lowest_score || 0)}%`;
  }

  showView('feedbackView');
}

async function loadCurriculum() {
  const container = document.getElementById('curriculumJourneyContainer');
  if (!container) return;
  
  try {
    const res = await fetch('/static/curriculum.json');
    if (!res.ok) throw new Error('Failed to load curriculum');
    const data = await res.json();
    
    container.innerHTML = '';
    
    const icons = [
      'settings_suggest',
      'database',
      'hub',
      'psychology',
      'forum',
      'smart_toy',
      'verified_user',
      'rocket_launch'
    ];
    
    data.modules.forEach((mod, idx) => {
      const startDay = mod.days[0];
      const endDay = mod.days[1];
      const modDays = data.days.filter(d => d.day >= startDay && d.day <= endDay);
      
      const card = document.createElement('div');
      card.className = 'glass-panel p-6 rounded-2xl border border-white/5 flex flex-col justify-between glass-panel-hover text-left';
      
      let daysHtml = modDays.slice(0, 3).map(d => `
        <div class="flex items-start gap-2 text-xs text-on-surface-variant">
          <span class="text-primary font-bold min-w-[32px]">D${d.day.toString().padStart(2, '0')}</span>
          <span class="text-left line-clamp-1">${d.title}</span>
        </div>
      `).join('');
      
      if (modDays.length > 3) {
        daysHtml += `
          <div class="text-[10px] text-primary/70 font-semibold pl-[40px]">+ ${modDays.length - 3} more topics</div>
        `;
      }
      
      const icon = icons[idx % icons.length];
      
      card.innerHTML = `
        <div>
          <div class="flex justify-between items-center mb-4">
            <span class="text-[10px] text-outline uppercase tracking-wider font-extrabold">Module 0${mod.n}</span>
            <span class="material-symbols-outlined text-primary text-xl">${icon}</span>
          </div>
          <h3 class="font-extrabold text-sm text-on-surface mb-3 line-clamp-1">${mod.title}</h3>
          <div class="space-y-2 border-t border-white/5 pt-3">
            ${daysHtml}
          </div>
        </div>
        <div class="mt-4 text-[10px] text-outline">
          Days ${startDay} - ${endDay}
        </div>
      `;
      container.appendChild(card);
    });
  } catch (e) {
    console.error('Failed to load curriculum journey:', e);
    container.innerHTML = '<p class="text-xs text-red-400">Failed to load cohort curriculum.</p>';
  }
}

window.onload = () => {
  showView('landingView');
  loadCandidates();
  loadCurriculum();
};
