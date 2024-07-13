from django.db.models.functions import TruncDate
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from django.db.models import Count, Sum
from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard

from db_api import models


class AnalyticsModule(modules.DashboardModule):
    title = 'Экран аналитики'
    template = 'admin/analytics.html'

    def init_with_context(self, context):
        start_date = date.today().replace(day=1)
        queryset = models.Profile.objects \
            .filter(created_at__gte=start_date) \
            .annotate(date=TruncDate('created_at')) \
            .values('date') \
            .annotate(amount=Count('id')) \
            .order_by('date')
        self.children = {
            'dates': [q['date'] for q in queryset],
            'amount': [q['amount'] for q in queryset],
        }
        self._initialized = True




class CustomIndexDashboard(Dashboard):
    title = 'Админка'
    
    def init_with_context(self, context):
        self.children.append(AnalyticsModule())
        
        self.children.append(modules.AppList(
            'Приложения',
            exclude=('django.contrib.*',),
        ))

        self.children.append(modules.AppList(
            'Администрирование',
            models=('django.contrib.*',),
        ))

        self.children.append(modules.RecentActions('Недавние действия', 5))


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(self.app_title, self.models),
            modules.RecentActions(
                'Недавние действия',
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)
