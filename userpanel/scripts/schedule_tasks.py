from django_q.models import Schedule

def run():
 Schedule.objects.create(
    func='userpanel.tasks',  
    schedule_type=Schedule.MINUTES,     
    minutes=2,                          
    repeats=-1,                          
)
