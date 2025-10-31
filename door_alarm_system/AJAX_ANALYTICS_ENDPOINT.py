"""
API endpoint for fetching updated analytics data via AJAX
This allows real-time updates without full page reload
"""

# Add this route to app.py to enable AJAX analytics updates

@app.route('/api/analytics/data')
@login_required
def get_analytics_data():
    """
    Returns analytics data in JSON format for AJAX updates
    This allows the frontend to update charts without page reload
    """
    if 'analytics' not in current_user.permissions.split(','):
        return jsonify({'error': 'Unauthorized'}), 403
    
    from sqlalchemy import func, and_
    
    # Get time range from request
    time_range = request.args.get('range', 'month')
    
    today = date.today()
    if time_range == 'day':
        start_date = today
    elif time_range == 'week':
        start_date = today - timedelta(days=7)
    else:  # month
        start_date = today - timedelta(days=30)
    
    # Door events
    door_events = EventLog.query.filter(
        and_(
            EventLog.timestamp >= start_date,
            EventLog.event_type.in_(['door_open', 'door_close'])
        )
    ).order_by(EventLog.timestamp.asc()).all()
    
    # Calculate door metrics (simplified version)
    door_open_count_day = 0
    door_open_count_week = 0
    door_open_count_month = 0
    
    for event in door_events:
        if event.event_type == 'door_open':
            event_date = event.timestamp.date()
            if event_date == today:
                door_open_count_day += 1
            if event_date >= today - timedelta(days=7):
                door_open_count_week += 1
            if event_date >= today - timedelta(days=30):
                door_open_count_month += 1
    
    # Alarm events
    alarm_events = EventLog.query.filter(
        and_(
            EventLog.timestamp >= start_date,
            EventLog.event_type == 'alarm_triggered'
        )
    ).order_by(EventLog.timestamp.asc()).all()
    
    total_alarms = len(alarm_events)
    
    # Get timer threshold
    timer_setting = Setting.query.filter_by(key='timer_duration').first()
    alarm_threshold = int(timer_setting.value) if timer_setting else 30
    
    # Calculate alarm metrics
    alarm_durations = []
    unacknowledged_alarms = 0
    
    for alarm_event in alarm_events:
        alarm_time = alarm_event.timestamp
        next_close = EventLog.query.filter(
            and_(
                EventLog.timestamp > alarm_time,
                EventLog.event_type == 'door_close'
            )
        ).order_by(EventLog.timestamp.asc()).first()
        
        if next_close:
            alarm_duration = (next_close.timestamp - alarm_time).total_seconds()
            alarm_durations.append(alarm_duration)
            
            if alarm_duration > (alarm_threshold * 2):
                unacknowledged_alarms += 1
        else:
            unacknowledged_alarms += 1
    
    avg_alarm_duration = sum(alarm_durations) / len(alarm_durations) if alarm_durations else 0
    longest_alarm_duration = max(alarm_durations) if alarm_durations else 0
    
    # MTTR
    mttr = avg_alarm_duration
    
    # Compliance
    compliant = sum(1 for d in alarm_durations if d <= (alarm_threshold * 2))
    total_compliance = len(alarm_durations) + unacknowledged_alarms
    compliance_percentage = (compliant / total_compliance * 100) if total_compliance > 0 else 100
    
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'time_range': time_range,
        'door_metrics': {
            'door_open_count_day': door_open_count_day,
            'door_open_count_week': door_open_count_week,
            'door_open_count_month': door_open_count_month
        },
        'alarm_metrics': {
            'total_alarms': total_alarms,
            'avg_alarm_duration': round(avg_alarm_duration, 1),
            'longest_alarm_duration': round(longest_alarm_duration, 1),
            'unacknowledged_alarms': unacknowledged_alarms
        },
        'performance_metrics': {
            'mttr': round(mttr, 1),
            'compliance_percentage': round(compliance_percentage, 2),
            'alarm_threshold': alarm_threshold
        }
    })
