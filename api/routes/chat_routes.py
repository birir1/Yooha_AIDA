# ============================================================
# chat_routes.py
# PRODUCTION MEMORY-AUGMENTED CHAT API
# FULLY STABILIZED + SESSION TIMELINE + EMOTION ANALYTICS READY
# ============================================================

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import traceback
import logging
import uuid

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)

# ============================================================
# SESSION ID GENERATOR (NEW CORE FEATURE)
# ============================================================

def generate_session_id(user_id: str = "anonymous"):
    """
    Timestamp-based session ID for analytics + emotion tracking
    Format: YYYYMMDD_HHMMSS_uuid
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:6]
    return f"{timestamp}_{user_id}_{short_uuid}"


def get_or_create_session(session_id=None, user_id="anonymous"):
    """
    Ensures stable session identity across chat lifecycle
    """
    if session_id:
        return session_id
    return generate_session_id(user_id)


# ============================================================
# RESPONSE HELPERS
# ============================================================

def success(data, code: int = 200):
    return jsonify({
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }), code


def error(message: str, code: int = 400, trace=None):
    payload = {
        "status": "error",
        "timestamp": datetime.utcnow().isoformat(),
        "message": message
    }
    if trace:
        payload["trace"] = trace
    return jsonify(payload), code


# ============================================================
# MEMORY SERIALIZER
# ============================================================

def serialize_memories(memories):
    results = []
    if not memories:
        return results

    for memory in memories:
        try:
            if isinstance(memory, dict):
                results.append({
                    "id": memory.get("id"),
                    "content": memory.get("memory") or memory.get("content") or str(memory),
                    "score": float(memory.get("score", 0.0)),
                    "timestamp": memory.get("timestamp")
                })
            else:
                results.append({"content": str(memory)})
        except Exception:
            continue

    return results


# ============================================================
# MEMORY RETRIEVAL
# ============================================================

def retrieve_memories(memory_manager, query, session_id, top_k):
    try:
        if memory_manager is None:
            return []

        if hasattr(memory_manager, "retrieve_memory"):
            return memory_manager.retrieve_memory(
                session_id=session_id,
                query=query,
                top_k=top_k
            ) or []

        if hasattr(memory_manager, "retrieve_memories"):
            return memory_manager.retrieve_memories(
                query=query,
                top_k=top_k
            ) or []

        return []

    except Exception as e:
        logger.exception(f"Memory retrieval failed: {e}")
        return []


# ============================================================
# CONTEXT BUILDER
# ============================================================

def build_context(memory_manager, session_id, memories):
    try:
        if memory_manager is None:
            return ""

        if hasattr(memory_manager, "build_context_window"):
            return memory_manager.build_context_window(
                session_id=session_id,
                retrieved_memories=memories
            )

        if hasattr(memory_manager, "build_context"):
            return memory_manager.build_context(memories)

        return "\n".join(
            str(m.get("memory") or m.get("content") or m)
            if isinstance(m, dict) else str(m)
            for m in memories
        )

    except Exception as e:
        logger.exception(f"Context building failed: {e}")
        return ""


# ============================================================
# SAVE MEMORY + EMOTION TIMELINE (NEW STRUCTURE)
# ============================================================

def save_interaction(
    memory_manager,
    session_id,
    user_id,
    user_message,
    assistant_response,
    emotion
):
    try:
        if memory_manager is None:
            logger.warning("No memory manager configured")
            return

        timestamp = datetime.utcnow().isoformat()

        memory_payload = {
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "type": "conversation",
            "emotion_event": {
                "emotion": emotion,
                "timestamp": timestamp
            },
            "user_message": user_message,
            "assistant_response": assistant_response
        }

        logger.info(f"💾 Saving interaction memory for session={session_id}")

        if hasattr(memory_manager, "store_memory"):
            try:
                memory_manager.store_memory(
                    session_id=session_id,
                    user_id=user_id,
                    memory=str(memory_payload),
                    metadata=memory_payload
                )
                return
            except TypeError:
                memory_manager.store_memory(
                    session_id=session_id,
                    memory=str(memory_payload)
                )
                return

        if hasattr(memory_manager, "add_memory"):
            try:
                memory_manager.add_memory(
                    session_id=session_id,
                    content=str(memory_payload),
                    metadata=memory_payload
                )
                return
            except TypeError:
                memory_manager.add_memory(str(memory_payload))
                return

        if hasattr(memory_manager, "save"):
            memory_manager.save(str(memory_payload), metadata=memory_payload)
            return

        logger.warning("⚠️ No compatible memory save method found")

    except Exception as e:
        logger.exception(f"Failed saving interaction memory: {e}")


# ============================================================
# SAFE AI GENERATION
# ============================================================

def safe_generate(llm_service, rag_pipeline, user_message,
                   session_id, user_id, context, emotion,
                   memories, top_k):

    try:
        rag_context = context

        if rag_pipeline and hasattr(rag_pipeline, "run"):
            try:
                retrieval_results = [
                    {
                        "content": m.get("memory") or m.get("content") or str(m),
                        "score": float(m.get("score", 0.5))
                    } if isinstance(m, dict) else {"content": str(m), "score": 0.5}
                    for m in memories
                ]

                rag_result = rag_pipeline.run(
                    user_message=user_message,
                    memory_results=retrieval_results,
                    retrieval_results=retrieval_results,
                    context={
                        "session_id": session_id,
                        "user_id": user_id
                    }
                )

                if isinstance(rag_result, dict):
                    rag_context = rag_result.get("context_block") or context

            except Exception as e:
                logger.exception(f"RAG failed: {e}")

        if llm_service and hasattr(llm_service, "generate_response"):
            response = llm_service.generate_response(
                user_message=user_message,
                context=rag_context,
                emotion=emotion,
                memories=memories
            )
            if response:
                return str(response).strip()

        if llm_service and hasattr(llm_service, "generate"):
            return str(llm_service.generate(
                prompt=user_message,
                context=rag_context
            ))

        return {
            "sadness": "I'm here with you. Want to talk about it?",
            "fear": "You're not alone. We can go step by step.",
            "anger": "That sounds frustrating. Tell me more.",
            "joy": "That sounds great — tell me more!",
            "surprise": "That’s unexpected — what happened?",
            "neutral": "I'm here with you. Tell me more."
        }.get(emotion, "I'm here with you.")

    except Exception as e:
        logger.exception(f"Generation failed: {e}")
        return "I'm still here with you."


# ============================================================
# CHAT ENDPOINT
# ============================================================

@chat_bp.route("/", methods=["POST"], strict_slashes=False)
def chat():
    try:
        if not request.is_json:
            return error("Content-Type must be application/json", 400)

        data = request.get_json() or {}

        user_message = str(data.get("message", "")).strip()
        user_id = str(data.get("user_id", "anonymous"))

        session_id = get_or_create_session(
            data.get("session_id"),
            user_id
        )

        top_k = int(data.get("top_k", 5))

        if not user_message:
            return error("message required", 400)

        logger.info(f"💬 Incoming message from {user_id}: {user_message}")

        memory_manager = current_app.config.get("MEMORY_MANAGER")
        llm_service = current_app.config.get("LLM_SERVICE")
        rag_pipeline = current_app.config.get("RAG_PIPELINE")
        emotion_engine = current_app.config.get("EMOTION_DETECTOR")

        memories = retrieve_memories(memory_manager, user_message, session_id, top_k)
        context = build_context(memory_manager, session_id, memories)

        emotion = "neutral"

        try:
            if emotion_engine and hasattr(emotion_engine, "detect_emotion"):
                result = emotion_engine.detect_emotion(user_message)
                if isinstance(result, dict):
                    emotion = result.get("emotion", "neutral")
                elif isinstance(result, str):
                    emotion = result
        except Exception as e:
            logger.warning(f"Emotion detection failed: {e}")

        response = safe_generate(
            llm_service,
            rag_pipeline,
            user_message,
            session_id,
            user_id,
            context,
            emotion,
            memories,
            top_k
        )

        save_interaction(
            memory_manager,
            session_id,
            user_id,
            user_message,
            response,
            emotion
        )

        return success({
            "session_id": session_id,
            "user_id": user_id,
            "response": str(response),
            "emotion": emotion,
            "memory_count": len(memories),
            "memories": serialize_memories(memories),
            "context": context
        })

    except Exception as e:
        logger.exception(f"Chat failed: {e}")
        return error(str(e), 500, traceback.format_exc())


# ============================================================
# HEALTH
# ============================================================

@chat_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "chat_routes",
        "session_model": "timestamp_uuid",
        "emotion_tracking": "enabled"
    })


@chat_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({
        "status": "ok",
        "message": "Chat routes operational"
    })