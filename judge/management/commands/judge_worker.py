import time
import logging
from django.core.management.base import BaseCommand
from judge.tasks import process_judge_queue

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '判题工作进程'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=2,
            help='处理间隔时间（秒）'
        )
        parser.add_argument(
            '--max-iterations',
            type=int,
            default=None,
            help='最大迭代次数（None表示无限循环）'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        max_iterations = options['max_iterations']
        
        self.stdout.write(
            self.style.SUCCESS(f'判题工作进程启动，间隔: {interval}秒')
        )
        
        iteration = 0
        total_processed = 0
        
        try:
            while True:
                if max_iterations and iteration >= max_iterations:
                    break
                
                # 处理判题队列
                processed = process_judge_queue()
                total_processed += processed
                
                if processed > 0:
                    self.stdout.write(
                        f'处理了 {processed} 个提交，总计: {total_processed}'
                    )
                
                iteration += 1
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n判题工作进程已停止')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'判题工作进程出错: {str(e)}')
            )
            logger.error(f'判题工作进程出错: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(f'判题工作进程结束，总共处理了 {total_processed} 个提交')
        )
