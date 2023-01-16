from dateutil import rrule
from datetime import date, timedelta, datetime


def get_holidays(a=date.today(), b=date.today()+timedelta(days=365)):
    rs = rrule.rruleset()
    # Include all potential holidays
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth= 1, bymonthday= 1))                     # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth= 1, bymonthday= 2, byweekday=rrule.MO)) # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth= 1, bymonthday= 3, byweekday=rrule.MO)) # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, byeaster= -2))                                  # Good Friday
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, byeaster= 1))                                   # Easter Monday
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth= 5, byweekday=rrule.MO, bysetpos=1))    # May Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth= 5, byweekday=rrule.MO, bysetpos=-1))   # Spring Bank Holiday
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth= 8, byweekday=rrule.MO, bysetpos=-1))   # Late Summer Bank Holiday
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=25))                     # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=26, byweekday=rrule.MO)) # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=27, byweekday=rrule.MO)) # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=26))                     # Boxing Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=27, byweekday=rrule.MO)) # Boxing Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=27, byweekday=rrule.TU)) # Boxing Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=28, byweekday=rrule.MO)) # Boxing Day
    rs.rrule(rrule.rrule(rrule.YEARLY, dtstart=a, until=b, bymonth=12, bymonthday=28, byweekday=rrule.TU)) # Boxing Day
    # Exclude potential holidays that fall on weekends
    rs.exrule(rrule.rrule(rrule.WEEKLY, dtstart=a, until=b, byweekday=(rrule.SA,rrule.SU)))
    return rs


def get_workingdays(a=date.today(), b=date.today()+timedelta(days=365)):
    rs = rrule.rruleset()
    rs.rrule(rrule.rrule(rrule.DAILY, dtstart=a, until=b))                         # Get all days between a and b
    rs.exrule(rrule.rrule(rrule.WEEKLY, dtstart=a, byweekday=(rrule.SA,rrule.SU))) # Exclude weekends
    rs.exrule(get_holidays(a,b))                                                   # Exclude holidays
    return rs


if __name__ == "__main__":
    for dy in get_holidays(date.today(),date.today()):
                print (dy.strftime('    %a %d %b %Y'))

    for yr in range(2015,2025):
        print ("{0}\n====".format(yr))
        print ("Holidays")
        for dy in get_holidays(datetime(yr,1,1),datetime(yr,12,31)):
                print (dy.strftime('    %a %d %b %Y'))
        print ("Working Days")
        tdays = len(list(get_workingdays(datetime(yr,1,1),datetime(yr,12,31))))
        print ("    {0} working days in {1}".format(tdays, yr))
        print ("")
