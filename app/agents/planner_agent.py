import json
from typing import Dict, Any, Tuple, List, Set


def normalize_candidate_profile(cand: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize candidate JSON from either flat structure or candidate_profiles.json structure."""
    if "member" in cand:
        member = cand["member"]
        missions = cand.get("missions", [])
        signals = cand.get("signals", {})
        
        passed_missions = [m.get("title") for m in missions if m.get("passed")]
        
        return {
            "name": member.get("name", "Candidate"),
            "experience_years": member.get("yearsExperience", member.get("experience_years", 2)),
            "skills": passed_missions if passed_missions else [member.get("jobRole", "Software Engineering")],
            "education": member.get("education", "CS Degree"),
            "projects": [f"Completed {signals.get('missionsCompleted', len(passed_missions))} missions"],
            "current_role": member.get("jobRole", "Software Engineer"),
            "jobRole": member.get("jobRole", "Software Engineer"),
            "missions": missions,
            "signals": signals
        }
    else:
        return {
            "name": cand.get("name", "Candidate"),
            "experience_years": cand.get("experience_years", cand.get("yearsExperience", 2)),
            "skills": cand.get("skills", [cand.get("jobRole", "Engineering")]),
            "education": cand.get("education", "Engineering"),
            "projects": cand.get("projects", []),
            "current_role": cand.get("current_role", cand.get("jobRole", "Developer")),
            "jobRole": cand.get("jobRole", cand.get("current_role", "Developer")),
            "missions": cand.get("missions", []),
            "signals": cand.get("signals", {})
        }


def build_knowledge_map(normalized_profile: Dict[str, Any], curriculum: Dict[str, Any]) -> Dict[int, str]:
    """
    Step 3: Build Candidate Knowledge Map.
    For every curriculum day, classify it as Mastered, Learning, Weak, Skipped, or Unknown.
    """
    knowledge_map = {}
    missions = normalized_profile.get("missions", [])
    
    # Create helper dictionary mapping day number to mission object
    mission_by_day = {}
    for m in missions:
        day_num = m.get("day")
        if day_num is not None:
            mission_by_day[int(day_num)] = m

    for day_obj in curriculum.get("days", []):
        day_num = int(day_obj.get("day", 0))
        if not day_num:
            continue
            
        mission = mission_by_day.get(day_num)
        if mission:
            passed = mission.get("passed", False)
            skipped = mission.get("skipped", False)
            attempts = int(mission.get("attempts", 1))
            
            if passed:
                if attempts == 1:
                    knowledge_map[day_num] = "Mastered"
                elif attempts == 2:
                    knowledge_map[day_num] = "Learning"
                else:
                    knowledge_map[day_num] = "Weak"
            elif skipped:
                knowledge_map[day_num] = "Skipped"
            else:
                knowledge_map[day_num] = "Weak"  # Attempted but not passed
        else:
            knowledge_map[day_num] = "Unknown"
            
    return knowledge_map


def build_curriculum_graph(curriculum: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    """
    Step 1: Build Curriculum Graph from curriculum.json.
    Extract Days, Modules, Topics, Learning Objectives, Tools, and Dependencies.
    """
    graph = {}
    
    # Map day numbers to module info
    day_to_module = {}
    for mod in curriculum.get("modules", []):
        mod_num = mod.get("n", 1)
        mod_title = mod.get("title", "General")
        day_range = mod.get("days", [1, 31])
        for d in range(day_range[0], day_range[-1] + 1):
            day_to_module[d] = {"number": mod_num, "title": mod_title}

    for day_obj in curriculum.get("days", []):
        day_num = int(day_obj.get("day", 0))
        if not day_num:
            continue
            
        objectives = day_obj.get("objectives", [])
        tools = day_obj.get("tools", [])
        
        # Simple logical dependency: Day N depends on Day N-1 if they share a module
        dependencies = []
        if day_num > 1:
            prev_mod = day_to_module.get(day_num - 1, {}).get("number")
            curr_mod = day_to_module.get(day_num, {}).get("number")
            if prev_mod == curr_mod:
                dependencies.append(day_num - 1)

        graph[day_num] = {
            "day": day_num,
            "module": day_to_module.get(day_num, {"number": 1, "title": "Environment"}),
            "topic": day_obj.get("title", "Syllabus Topic"),
            "objectives": objectives,
            "tools": tools,
            "difficulty": "medium",  # default base difficulty
            "dependencies": dependencies
        }
        
    return graph


def plan_interview_agent(
    candidate_profile: Dict[str, Any],
    curriculum: Dict[str, Any],
    tech_spec: str
) -> Tuple[Dict[str, Any], list, str, int]:
    """
    Adaptive Interview Planner:
    - Builds internal curriculum graph and candidate knowledge map.
    - Generates a fully personalized interview plan starting from the candidate'scompleted passed missions
      with higher attempt counts (representing weaker understanding).
    """
    normalized_profile = normalize_candidate_profile(candidate_profile)
    curr_graph = build_curriculum_graph(curriculum)
    knowledge_map = build_knowledge_map(normalized_profile, curriculum)
    
    missions = normalized_profile.get("missions", [])
    
    # ── Choose the first interview topic (Step 4 Rules) ──
    # Choose from the candidate's passed missions, preferring higher attempts (weaker understanding)
    passed_missions = [m for m in missions if m.get("passed")]
    passed_missions.sort(key=lambda m: int(m.get("attempts", 1)), reverse=True)
    
    planned_topics = []
    used_days = set()
    used_modules = set()
    
    # 1. First topic: Weakest passed mission
    starting_day_num = None
    if passed_missions:
        first_mission = passed_missions[0]
        starting_day_num = int(first_mission.get("day"))
        day_info = curr_graph.get(starting_day_num)
        if day_info:
            planned_topics.append({
                "day": f"Day {starting_day_num}",
                "topic": day_info["topic"],
                "confidence": knowledge_map.get(starting_day_num, "Weak"),
                "priority": "high",
                "allocated_questions": 2,
                "objectives": day_info["objectives"],
                "tools": day_info["tools"],
                "module": day_info["module"],
                "reason": f"Completed mission with {first_mission.get('attempts', 1)} attempts. Weak confidence (probe weaker understanding first)."
            })
            used_days.add(starting_day_num)
            used_modules.add(day_info["module"]["number"])

    # 2. Add other passed missions (Learning / Mastered confidence) to show strength
    for mission in passed_missions[1:]:
        d_num = int(mission.get("day"))
        day_info = curr_graph.get(d_num)
        if day_info and d_num not in used_days:
            # Prefer different modules to satisfy breadth requirements
            mod_num = day_info["module"]["number"]
            if mod_num not in used_modules or len(used_days) < 3:
                planned_topics.append({
                    "day": f"Day {d_num}",
                    "topic": day_info["topic"],
                    "confidence": knowledge_map.get(d_num, "Mastered"),
                    "priority": "medium",
                    "allocated_questions": 2,
                    "objectives": day_info["objectives"],
                    "tools": day_info["tools"],
                    "module": day_info["module"],
                    "reason": f"Completed mission with {mission.get('attempts', 1)} attempts. Mastered/Learning confidence."
                })
                used_days.add(d_num)
                used_modules.add(mod_num)
                if len(planned_topics) >= 3:
                    break

    # 3. Add one skipped or unknown topic near the end to identify gaps
    # Never ask advanced questions on skipped topics (allocated_questions = 1 or basic level)
    skipped_days = [d for d, status in knowledge_map.items() if status in ["Skipped", "Unknown"] and d not in used_days]
    if skipped_days:
        # Choose a basic skipped topic (e.g. lower day number is typically more basic)
        skipped_days.sort()
        d_num = skipped_days[0]
        day_info = curr_graph.get(d_num)
        if day_info:
            planned_topics.append({
                "day": f"Day {d_num}",
                "topic": day_info["topic"],
                "confidence": knowledge_map.get(d_num, "Skipped"),
                "priority": "low",
                "allocated_questions": 2,  # Budget allocation
                "objectives": day_info["objectives"],
                "tools": day_info["tools"],
                "module": day_info["module"],
                "reason": "Knowledge gap identification (skipped or unknown curriculum topic)."
            })
            used_days.add(d_num)
            used_modules.add(day_info["module"]["number"])

    # Fallback to general days if we still don't have 4 distinct days
    if len(planned_topics) < 4:
        for d_num, day_info in curr_graph.items():
            if d_num not in used_days:
                planned_topics.append({
                    "day": f"Day {d_num}",
                    "topic": day_info["topic"],
                    "confidence": "Unknown",
                    "priority": "low",
                    "allocated_questions": 2,
                    "objectives": day_info["objectives"],
                    "tools": day_info["tools"],
                    "module": day_info["module"],
                    "reason": "Syllabus coverage baseline (curriculum day fallback)."
                })
                used_days.add(d_num)
                if len(planned_topics) >= 4:
                    break

    # Determine starting difficulty
    starting_diff = "medium"
    if starting_day_num:
        first_conf = knowledge_map.get(starting_day_num, "Weak")
        if first_conf == "Mastered":
            starting_diff = "medium_plus"
        elif first_conf == "Weak":
            starting_diff = "easy"
            
    # Senior candidates get a boost
    exp = float(normalized_profile.get("experience_years", 2))
    if exp >= 5 and starting_diff == "easy":
        starting_diff = "medium"
    elif exp >= 5 and starting_diff == "medium":
        starting_diff = "medium_plus"

    first_topic_name = planned_topics[0]['topic'] if planned_topics else 'General Fundamentals'
    first_attempts = passed_missions[0].get('attempts') if (passed_missions and planned_topics) else 1

    # Plan analysis breakdown
    analysis = {
        "strengths": [curr_graph[d]["topic"] for d in used_days if knowledge_map.get(d) in ["Mastered", "Learning"]],
        "gaps": [curr_graph[d]["topic"] for d in used_days if knowledge_map.get(d) in ["Skipped", "Unknown"]],
        "experience_level": "senior" if exp >= 5 else ("junior" if exp < 2 else "mid"),
        "priority_topics": [t["topic"] for t in planned_topics],
        "reasoning": f"Planning interview for {normalized_profile.get('name')} based on {len(missions)} candidate missions. "
                     f"Starting with {first_topic_name} (attempts: {first_attempts}) "
                     f"to probe weaker understanding, covering {len(used_days)} distinct curriculum days."
    }
    
    return analysis, planned_topics, starting_diff, 8
