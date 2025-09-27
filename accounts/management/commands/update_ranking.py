from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserRanking

User = get_user_model()


class Command(BaseCommand):
    help = '更新用户排行榜'

    def handle(self, *args, **options):
        self.stdout.write('开始更新用户排行榜...')
        
        # 获取所有用户，按积分排序
        users = User.objects.filter(is_active=True).order_by('-rating', 'accepted_submissions')
        
        for index, user in enumerate(users, 1):
            # 更新或创建排行榜记录
            ranking, created = UserRanking.objects.get_or_create(
                user=user,
                defaults={
                    'rank': index,
                    'rating': user.rating,
                    'solved_count': user.accepted_submissions,
                }
            )
            
            if not created:
                # 更新现有记录
                ranking.rank = index
                ranking.rating = user.rating
                ranking.solved_count = user.accepted_submissions
                ranking.save()
            
            if index <= 10:  # 只显示前10名
                self.stdout.write(f'第{index}名: {user.username} (积分: {user.rating})')
        
        self.stdout.write(
            self.style.SUCCESS(f'排行榜更新完成！共更新了 {users.count()} 个用户')
        )
