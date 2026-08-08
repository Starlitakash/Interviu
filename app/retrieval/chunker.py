from typing import List, Dict, Any

def chunk_curriculum(curriculum: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Chunk curriculum JSON into per-topic documents with rich metadata.
    Supports both nested topics schema and flat days/objectives schema (curriculum.json).
    """
    chunks = []
    days = curriculum.get("days", [])
    
    for day_obj in days:
        day_num = str(day_obj.get("day", "1"))
        day_title = day_obj.get("title", f"Day {day_num}")
        day_key = f"Day {day_num}" if not str(day_num).startswith("Day") else str(day_num)
        
        topics = day_obj.get("topics", [])
        if topics:
            for topic in topics:
                topic_name = topic.get("name", day_title)
                content = topic.get("content", "")
                objectives = topic.get("learning_objectives", topic.get("objectives", []))
                concepts = topic.get("key_concepts", topic.get("tools", []))
                
                text_block = (
                    f"Curriculum Day: {day_key} ({day_title})\n"
                    f"Topic: {topic_name}\n"
                    f"Content: {content}\n"
                    f"Learning Objectives: {', '.join(objectives) if objectives else 'N/A'}\n"
                    f"Key Concepts & Tools: {', '.join(concepts) if concepts else 'N/A'}"
                )
                
                chunk = {
                    "id": f"{day_key}_{topic_name}".replace(" ", "_").lower(),
                    "text": text_block,
                    "metadata": {
                        "day": day_key,
                        "day_num": day_num,
                        "day_title": day_title,
                        "topic": topic_name,
                        "content": content,
                        "learning_objectives": objectives,
                        "key_concepts": concepts
                    }
                }
                chunks.append(chunk)
        else:
            # Format from curriculum.json (day title, objectives, tools)
            objectives = day_obj.get("objectives", [])
            tools = day_obj.get("tools", [])
            day_type = day_obj.get("type", "LEARNING")
            
            text_block = (
                f"Curriculum Day: {day_key} ({day_title}) [{day_type}]\n"
                f"Topic: {day_title}\n"
                f"Tools & Tech: {', '.join(tools) if tools else 'N/A'}\n"
                f"Learning Objectives:\n- " + "\n- ".join(objectives)
            )
            
            chunk = {
                "id": f"{day_key}_{day_title}".replace(" ", "_").lower(),
                "text": text_block,
                "metadata": {
                    "day": day_key,
                    "day_num": day_num,
                    "day_title": day_title,
                    "topic": day_title,
                    "content": "\n".join(objectives),
                    "learning_objectives": objectives,
                    "key_concepts": tools
                }
            }
            chunks.append(chunk)
            
    return chunks
