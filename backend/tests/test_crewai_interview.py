"""CrewAI u591a Agent u534fu540cu9762u8bd5u7cfbu7edfu6d4bu8bd5u811au672c

u6f14u793au5982u4f55u4f7fu7528 CrewAI u591a Agent u534fu540cu9762u8bd5u7cfbu7edf
"""
import asyncio
import logging
import pytest

from src.agents.interviewer_factory import InterviewerFactory
from src.services.ai.crewai_integration import crewai_integration

# u8bbeu7f6eu65e5u5fd7
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_crewai_available():
    """u6d4bu8bd5 CrewAI u662fu5426u53efu7528"""
    is_available = crewai_integration.is_available()
    logger.info(f"CrewAI u662fu5426u53efu7528: {is_available}")
    assert isinstance(is_available, bool)


@pytest.mark.asyncio
async def test_get_coordinator():
    """u6d4bu8bd5u83b7u53d6u9762u8bd5u534fu8c03u5458"""
    coordinator = InterviewerFactory.get_interviewer("coordinator")
    logger.info(f"u9762u8bd5u534fu8c03u5458: {coordinator.name} ({coordinator.role})")
    assert coordinator.interviewer_id == "coordinator"


@pytest.mark.asyncio
async def test_interview_round():
    """u6d4bu8bd5u5355u8f6eu9762u8bd5"""
    if not crewai_integration.is_available():
        pytest.skip("CrewAI u4e0du53efu7528uff0cu8df3u8fc7u6d4bu8bd5")
    
    # u6a21u62dfu9762u8bd5u5386u53f2u8bb0u5f55
    messages = [
        {"sender_type": "interviewer", "sender_name": "u9762u8bd5u534fu8c03u5458", "content": "u4f60u597duff0cu6b22u8fceu53c2u52a0u6211u4eecu7684u9762u8bd5u3002u8bf7u7b80u5355u4ecbu7ecdu4e00u4e0bu4f60u81eau5df1u548cu4f60u7684u5de5u4f5cu7ecfu9a8cu3002"},
        {"sender_type": "user", "content": "u4f60u597duff0cu6211u662fu674eu660euff0cu4e00u540du8f6fu4ef6u5de5u7a0bu5e08uff0cu6709 5 u5e74u7684u5de5u4f5cu7ecfu9a8cu3002u6211u64c5u957f React u548c Node.js u5f00u53d1uff0cu66feu7ecfu53c2u4e0eu8fc7u591au4e2au5927u578b Web u5e94u7528u7684u5f00u53d1u3002"}
    ]
    
    result = await crewai_integration.conduct_interview_round(
        interviewer_type="technical",
        messages=messages,
        position="u524du7aefu5f00u53d1u5de5u7a0bu5e08",
        difficulty="medium"
    )
    
    logger.info(f"u9762u8bd5u5b98u56deu590d: {result}")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_full_interview():
    """u6d4bu8bd5u5b8cu6574u9762u8bd5u6d41u7a0b"""
    if not crewai_integration.is_available():
        pytest.skip("CrewAI u4e0du53efu7528uff0cu8df3u8fc7u6d4bu8bd5")
    
    # u83b7u53d6u9762u8bd5u534fu8c03u5458
    coordinator = InterviewerFactory.get_interviewer("coordinator")
    
    # u6a21u62dfu7b80u5386
    resume = """u674eu660e
u524du7aefu5f00u53d1u5de5u7a0bu5e08 | 5u5e74u5de5u4f5cu7ecfu9a8c

u6280u80fdu6982u8981uff1a
- u7cbeu901a React, Vue.js, Node.js
- u719fu6089 TypeScript, JavaScript, HTML, CSS
- u719fu6089u524du7aefu6027u80fdu4f18u5316u548cu7528u6237u4f53u9a8cu8bbeu8ba1

u5de5u4f5cu7ecfu9a8cuff1a
1. ABCu79d1u6280u516cu53f8 (2020-u81f3u4eca)
   - u9ad8u7ea7u524du7aefu5f00u53d1u5de5u7a0bu5e08
   - u8d1fu8d23u516cu53f8u6838u5fc3u4ea7u54c1u524du7aefu67b6u6784u8bbeu8ba1u548cu5f00u53d1
   - u5e26u9886 5 u4ebau56e2u961fu5b8cu6210u591au4e2au5173u952eu9879u76ee

2. XYZu516cu53f8 (2018-2020)
   - u524du7aefu5f00u53d1u5de5u7a0bu5e08
   - u8d1fu8d23u516cu53f8u7535u5546u5e73u53f0u7684u524du7aefu5f00u53d1u548cu7ef4u62a4
   
u6559u80b2u80ccu666fuff1a
- u8ba1u7b97u673au79d1u5b66u4e0eu6280u672fu672cu79d1, u67d0u5927u5b66, 2018u5e74u6bd5u4e1a
"""
    
    # u6267u884cu5b8cu6574u9762u8bd5u6d41u7a0b
    result = await coordinator.start_interview(
        position="u9ad8u7ea7u524du7aefu5f00u53d1u5de5u7a0bu5e08",
        difficulty="hard",
        resume=resume
    )
    
    logger.info(f"u9762u8bd5u7ed3u679c: {result}")
    assert isinstance(result, dict)
    assert "status" in result


# u5982u679cu76f4u63a5u8fd0u884cu811au672c

def run_tests():
    """u76f4u63a5u8fd0u884cu6d4bu8bd5"""
    asyncio.run(test_crewai_available())
    asyncio.run(test_get_coordinator())
    
    # u5982u679c CrewAI u53efu7528uff0cu8fd0u884cu5b8cu6574u6d4bu8bd5
    if crewai_integration.is_available():
        asyncio.run(test_interview_round())
        asyncio.run(test_full_interview())
    else:
        logger.warning("CrewAI u4e0du53efu7528uff0cu8df3u8fc7 CrewAI u6d4bu8bd5")


if __name__ == "__main__":
    run_tests()
