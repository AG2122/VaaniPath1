"""VaniPath - Adaptive Assessment Engine"""
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone

from app.services.worksheet_service import QUESTION_BANK


class AssessmentService:
    """Adaptive assessment engine with learning cycle: TEACH → PRACTICE → ASSESS → ADAPT."""

    def generate(self, student_id: Optional[str], subject: str, topic: str,
                 grade: int = 2, question_count: int = 10, language: str = "sat") -> Dict:
        """Generate an adaptive assessment."""
        # Pull questions from the worksheet bank
        subject_bank = QUESTION_BANK.get(subject, {})
        questions = []

        for t, qs in subject_bank.items():
            if t.lower() == topic.lower() or topic.lower() in t.lower():
                questions.extend(qs)
                break

        if not questions:
            # Use any available questions for the subject
            for t, qs in subject_bank.items():
                questions.extend(qs)

        # Limit and format
        if len(questions) > question_count:
            import random
            questions = random.sample(questions, question_count)
        else:
            questions = questions[:question_count]

        assessment_questions = []
        for i, q in enumerate(questions, 1):
            q_id = str(uuid.uuid4())
            assessment_questions.append({
                "id": q_id,
                "question_number": i,
                "question_type": q.get("type", "mcq"),
                "hindi_text": q["hindi"],
                "santhali_text": q["santhali"],
                "options": q.get("options", []),
                "correct_answer": q["answer"],
                "topic": topic,
            })

        assessment_id = str(uuid.uuid4())

        return {
            "assessment_id": assessment_id,
            "student_id": student_id,
            "subject": subject,
            "topic": topic,
            "grade": grade,
            "total_questions": len(assessment_questions),
            "language": language,
            "questions": assessment_questions,
            "status": "pending",
        }

    def submit(self, assessment_id: str, answers: List[Dict[str, str]],
               questions: List[Dict]) -> Dict:
        """Submit assessment answers and get results with adaptive recommendations."""
        correct = 0
        wrong = 0
        topic_scores = {}
        results = []

        for answer_entry in answers:
            q_id = answer_entry.get("question_id", "")
            student_answer = answer_entry.get("answer", "")

            # Find the matching question
            question = None
            for q in questions:
                if q["id"] == q_id:
                    question = q
                    break

            if question is None:
                continue

            is_correct = student_answer.strip() == question["correct_answer"].strip()

            if is_correct:
                correct += 1
            else:
                wrong += 1

            topic = question.get("topic", "general")
            if topic not in topic_scores:
                topic_scores[topic] = {"correct": 0, "total": 0}
            topic_scores[topic]["total"] += 1
            if is_correct:
                topic_scores[topic]["correct"] += 1

            results.append({
                "question_id": q_id,
                "question": question.get("hindi_text", ""),
                "student_answer": student_answer,
                "correct_answer": question["correct_answer"],
                "is_correct": is_correct,
                "topic": topic,
            })

        total = correct + wrong
        score = (correct / total * 100) if total > 0 else 0

        # Analyze weak and strong topics
        weak_topics = []
        strong_topics = []
        for topic, stats in topic_scores.items():
            if stats["total"] > 0:
                topic_score = stats["correct"] / stats["total"]
                if topic_score < 0.6:
                    weak_topics.append({"topic": topic, "score": round(topic_score * 100, 1)})
                elif topic_score >= 0.8:
                    strong_topics.append({"topic": topic, "score": round(topic_score * 100, 1)})

        # Generate adaptive recommendations
        recommendations = self._generate_recommendations(weak_topics, strong_topics, score)

        return {
            "assessment_id": assessment_id,
            "score": round(score, 1),
            "correct_answers": correct,
            "wrong_answers": wrong,
            "total_questions": total,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "results": results,
            "recommendations": recommendations,
            "learning_cycle": {
                "teach": f"Review concepts in weak areas: {[t['topic'] for t in weak_topics]}",
                "practice": "Use flashcards for visual learning of weak topics",
                "assess": "Take another assessment after practice",
                "adapt": "Focus on the weakest areas first",
            },
        }

    def _generate_recommendations(self, weak_topics: List, strong_topics: List,
                                   score: float) -> List[Dict]:
        """Generate adaptive recommendations based on assessment results."""
        recommendations = []

        for wt in weak_topics:
            topic = wt["topic"]
            if score < 40:
                recommendations.append({
                    "activity_type": "flashcard",
                    "title": f"Practice {topic} with visual flashcards",
                    "description": f"Start with basic {topic} flashcards to build a strong foundation.",
                    "priority": 1,
                    "reason": f"Score below 40% in {topic}",
                })
            else:
                recommendations.append({
                    "activity_type": "worksheet",
                    "title": f"Additional {topic} worksheet practice",
                    "description": f"Practice more {topic} questions to improve from {wt['score']}%.",
                    "priority": 2,
                    "reason": f"Score {wt['score']}% in {topic}",
                })

        if not weak_topics and score >= 80:
            recommendations.append({
                "activity_type": "lesson",
                "title": "Advance to next topic",
                "description": "You've mastered this topic! Ready for the next challenge.",
                "priority": 3,
                "reason": "All topics mastered",
            })

        if score < 50:
            recommendations.append({
                "activity_type": "lesson",
                "title": "Review the lesson content",
                "description": "Re-read the lesson explanation and examples before trying again.",
                "priority": 1,
                "reason": "Overall score below 50%",
            })

        return recommendations

    def get_recommendations(self, student_id: str, weak_topics: List[Dict]) -> List[Dict]:
        """Get personalized recommendations for a student."""
        recommendations = []

        for wt in weak_topics:
            topic = wt.get("topic", "general")
            score = wt.get("score", 0)

            recommendations.append({
                "activity_type": "flashcard",
                "title": f"Practice {topic} Flashcards",
                "description": f"Visual flashcards to strengthen {topic} skills",
                "subject": "Mathematics",
                "topic": topic,
                "reason": f"Scored {score}% in {topic}",
                "priority": 1 if score < 50 else 2,
            })

            if score < 60:
                recommendations.append({
                    "activity_type": "worksheet",
                    "title": f"{topic} Worksheet",
                    "description": f"Additional practice questions for {topic}",
                    "subject": "Mathematics",
                    "topic": topic,
                    "reason": f"Needs more practice in {topic}",
                    "priority": 2,
                })

        return recommendations


# Global instance
assessment_service = AssessmentService()
