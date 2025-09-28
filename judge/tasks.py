import logging
from typing import Dict
from django.utils import timezone
from .models import JudgeQueue, JudgeResult
from .engine_factory import JudgeEngineFactory

logger = logging.getLogger(__name__)


def add_to_judge_queue(submission) -> JudgeQueue:
    """添加提交到判题队列"""
    try:
        # 创建队列项
        queue_item = JudgeQueue.objects.create(
            submission=submission,
            priority=0  # 可以根据用户等级等调整优先级
        )
        
        # 创建判题结果记录
        JudgeResult.objects.create(
            submission=submission,
            status='pending'
        )
        
        # 更新提交状态
        submission.status = 'pending'
        submission.save()
        
        logger.info(f"提交 {submission.id} 已加入判题队列")
        return queue_item
        
    except Exception as e:
        logger.error(f"添加提交到队列失败: {str(e)}")
        # 更新提交状态为系统错误
        submission.status = 'system_error'
        submission.error_message = f"加入队列失败: {str(e)}"
        submission.save()
        raise


def process_judge_queue():
    """处理判题队列"""
    try:
        # 获取待处理的队列项
        queue_items = JudgeQueue.objects.filter(
            status='pending'
        ).order_by('-priority', 'created_at')[:10]  # 每次处理10个
        
        if not queue_items.exists():
            return 0
        
        processed_count = 0
        judge_engine = JudgeEngineFactory.create_engine()
        
        for queue_item in queue_items:
            try:
                # 更新队列状态
                queue_item.status = 'processing'
                queue_item.started_at = timezone.now()
                queue_item.save()
                
                # 更新提交状态
                submission = queue_item.submission
                submission.status = 'judging'
                submission.save()
                
                # 执行判题
                result = judge_engine.judge_submission(submission)
                
                # 更新判题结果
                judge_result = JudgeResult.objects.get(submission=submission)
                judge_result.status = result['status']
                judge_result.score = result['score']
                judge_result.time_used = result.get('time_used')
                judge_result.memory_used = result.get('memory_used')
                judge_result.error_message = result.get('error_message') or ''
                judge_result.test_results = result.get('test_results', [])
                judge_result.save()
                
                # 更新提交记录
                submission.status = result['status']
                submission.time_used = result.get('time_used')
                submission.memory_used = result.get('memory_used')
                submission.score = result['score']
                submission.error_message = result.get('error_message') or ''
                submission.test_results = result.get('test_results', [])
                submission.save()
                
                # 更新题目统计
                problem = submission.problem
                problem.total_submissions += 1
                if result['status'] == 'accepted':
                    problem.accepted_submissions += 1
                problem.save()
                
                # 更新用户统计
                user = submission.user
                user.total_submissions += 1
                if result['status'] == 'accepted':
                    user.accepted_submissions += 1
                user.save()
                
                # 更新队列状态
                queue_item.status = 'completed'
                queue_item.completed_at = timezone.now()
                queue_item.save()
                
                processed_count += 1
                logger.info(f"提交 {submission.id} 判题完成，状态: {result['status']}")
                
            except Exception as e:
                logger.error(f"处理提交 {queue_item.submission.id} 失败: {str(e)}")
                
                # 更新状态为失败
                queue_item.status = 'failed'
                queue_item.error_message = str(e)
                queue_item.completed_at = timezone.now()
                queue_item.save()
                
                # 更新提交状态
                submission = queue_item.submission
                submission.status = 'system_error'
                submission.error_message = f"判题失败: {str(e)}"
                submission.save()
                
                # 更新判题结果
                try:
                    judge_result = JudgeResult.objects.get(submission=submission)
                    judge_result.status = 'system_error'
                    judge_result.error_message = f"判题失败: {str(e)}"
                    judge_result.save()
                except JudgeResult.DoesNotExist:
                    pass
        
        return processed_count
        
    except Exception as e:
        logger.error(f"处理判题队列失败: {str(e)}")
        return 0


def rejudge_submission(submission):
    """重新判题"""
    try:
        # 删除旧的队列项和结果
        JudgeQueue.objects.filter(submission=submission).delete()
        JudgeResult.objects.filter(submission=submission).delete()
        
        # 重新加入队列
        return add_to_judge_queue(submission)
        
    except Exception as e:
        logger.error(f"重新判题失败: {str(e)}")
        raise
