"""
Plotly chart factories for AI Wellness Buddy.

Each function returns a ``plotly.graph_objects.Figure`` ready to be
rendered with ``st.plotly_chart(fig, width="stretch")``.

A consistent calming colour palette and Inter font are used across
all charts for a research-grade presentation.
"""

import plotly.graph_objects as go

# -----------------------------------------------------------------------
# Shared palette & layout helpers
# -----------------------------------------------------------------------

_FONT = dict(family='Inter')
_HOVER = dict(bgcolor='#fff', font_size=12, font_family='Inter')
_TRANSPARENT = 'rgba(0,0,0,0)'
_TRANSITION_DURATION = 500
_TRANSITION_EASING = 'cubic-in-out'

EMO_COLORS = {
    'joy': '#4DD0E1', 'positive': '#4DD0E1',
    'neutral': '#9B8CFF',
    'sadness': '#5B8CFF', 'negative': '#5B8CFF',
    'anger': '#FF8A65',
    'fear': '#FFB74D', 'anxiety': '#FFB74D',
    'crisis': '#EF5350', 'distress': '#EF5350',
}

_GAUGE_COLORS = {
    'low': '#5B8CFF',
    'medium': '#FFB74D',
    'high': '#EF5350',
    'critical': '#D32F2F',
}


def _base_layout(height=320, **overrides):
    """Return a dict of common layout properties."""
    props = dict(
        template='plotly_white',
        height=height,
        margin=dict(l=40, r=20, t=20, b=40),
        paper_bgcolor=_TRANSPARENT,
        plot_bgcolor=_TRANSPARENT,
        font=_FONT,
        hoverlabel=_HOVER,
    )
    props.update(overrides)
    return props


# -----------------------------------------------------------------------
# Chart creation functions
# -----------------------------------------------------------------------

def create_sentiment_chart(sentiments: list) -> go.Figure:
    """Current-session sentiment line chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=sentiments,
        mode='lines+markers',
        name='Sentiment',
        line=dict(color='#5B8CFF', width=3, shape='spline'),
        marker=dict(size=7, color='#9B8CFF', line=dict(color='#fff', width=1)),
        fill='tozeroy',
        fillcolor='rgba(91,140,255,0.12)',
        hovertemplate='Message %{x}<br>Sentiment: %{y:.2f}<extra></extra>',
    ))
    fig.update_layout(**_base_layout(xaxis_title='Message #', yaxis_title='Sentiment'))
    return fig


def create_moving_average_chart(ma: list) -> go.Figure:
    """Small moving-average companion chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=ma,
        mode='lines',
        name='3-msg MA',
        line=dict(color='#FF8A65', width=2, dash='dot'),
    ))
    fig.update_layout(**_base_layout(
        height=220, margin=dict(l=30, r=10, t=10, b=30),
    ))
    return fig


def create_emotion_donut(emotions: list, counts: list,
                         colors: list | None = None) -> go.Figure:
    """Donut (pie with hole) chart for emotion distribution."""
    if colors is None:
        colors = [EMO_COLORS.get(e, '#9B8CFF') for e in emotions]
    fig = go.Figure(go.Pie(
        labels=[e.capitalize() for e in emotions],
        values=counts,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=12),
        hoverinfo='label+value+percent',
        pull=[0.03] * len(emotions),
    ))
    fig.update_layout(**_base_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        annotations=[dict(
            text='Emotions', x=0.5, y=0.5,
            font=dict(size=14, color='#64748B'),
            showarrow=False,
        )],
    ))
    return fig


def create_emotion_probability_bar(probabilities: dict) -> go.Figure:
    """Horizontal bar chart for emotion probability distribution.

    *probabilities* maps emotion labels to float values in [0, 1].
    Bars are sorted descending so the most likely emotion appears first.
    """
    if not probabilities:
        probabilities = {'neutral': 1.0}
    sorted_items = sorted(probabilities.items(), key=lambda kv: kv[1], reverse=True)
    labels = [e.capitalize() for e, _ in sorted_items]
    values = [v for _, v in sorted_items]
    colors = [EMO_COLORS.get(e, '#9B8CFF') for e, _ in sorted_items]
    fig = go.Figure(go.Bar(
        y=labels,
        x=values,
        orientation='h',
        marker=dict(color=colors, line=dict(color='#ffffff', width=1)),
        text=[f'{v:.0%}' for v in values],
        textposition='outside',
        textfont=dict(size=11),
        hovertemplate='%{y}: %{x:.2%}<extra></extra>',
    ))
    fig.update_layout(**_base_layout(
        height=max(160, 28 * len(labels)),
        xaxis=dict(range=[0, 1.12], showgrid=False, zeroline=False,
                   showticklabels=False),
        yaxis=dict(autorange='reversed', showgrid=False),
        margin=dict(l=80, r=40, t=10, b=10),
    ))
    return fig


def create_risk_gauge(risk_score: float, risk_level: str = 'low') -> go.Figure:
    """Semi-circular animated risk dial."""
    bar_color = _GAUGE_COLORS.get(risk_level, '#5B8CFF')
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=risk_score,
        title={'text': '<b>Risk Score</b>',
               'font': {'size': 18, 'color': '#64748B', 'family': 'Inter'}},
        number={'suffix': ' / 1.00',
                'font': {'size': 32, 'color': '#334155', 'family': 'Inter'}},
        delta={'reference': 0.25,
               'increasing': {'color': '#EF5350'},
               'decreasing': {'color': '#5B8CFF'}},
        gauge={
            'axis': {
                'range': [0, 1],
                'tickwidth': 1,
                'tickcolor': '#94a3b8',
                'tickvals': [0, 0.25, 0.5, 0.75, 1.0],
                'ticktext': ['Safe', 'Low', 'Med', 'High', 'Crit'],
                'tickfont': {'size': 10, 'color': '#94a3b8'},
            },
            'bar': {'color': bar_color, 'thickness': 0.82},
            'bgcolor': _TRANSPARENT,
            'borderwidth': 0,
            'steps': [
                {'range': [0, 0.25], 'color': 'rgba(91,140,255,0.10)'},
                {'range': [0.25, 0.50], 'color': 'rgba(255,183,77,0.10)'},
                {'range': [0.50, 0.75], 'color': 'rgba(239,83,80,0.10)'},
                {'range': [0.75, 1.0], 'color': 'rgba(211,47,47,0.12)'},
            ],
            'threshold': {
                'line': {'color': '#D32F2F', 'width': 3},
                'thickness': 0.85,
                'value': risk_score,
            },
        },
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=50, b=10),
        paper_bgcolor=_TRANSPARENT,
        font=_FONT,
    )
    return fig


def create_history_chart(hist_data: list,
                         forecast: dict | None = None) -> go.Figure:
    """30-day historical sentiment line with optional forecast overlay."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=hist_data,
        mode='lines+markers',
        name='Mood',
        line=dict(color='#9B8CFF', width=3, shape='spline'),
        marker=dict(size=6, color='#5B8CFF', line=dict(color='#fff', width=1)),
        fill='tozeroy',
        fillcolor='rgba(155,140,255,0.10)',
        hovertemplate='Session %{x}<br>Avg Mood: %{y:.2f}<extra></extra>',
    ))

    if forecast:
        pred_val = forecast['predicted_value']
        fig.add_trace(go.Scatter(
            x=[len(hist_data) - 1, len(hist_data)],
            y=[hist_data[-1], pred_val],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='#FF8A65', width=2, dash='dash'),
            marker=dict(size=8, color='#FF8A65', symbol='diamond',
                        line=dict(color='#fff', width=1)),
            hovertemplate='Forecast<br>Predicted: %{y:.2f}<extra></extra>',
        ))

    fig.update_layout(**_base_layout(
        xaxis_title='Session', yaxis_title='Avg Mood',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                    xanchor='right', x=1),
    ))
    return fig


def create_risk_history_chart(risk_hist: list) -> go.Figure:
    """30-day risk level history."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=risk_hist,
        mode='lines+markers',
        name='Risk',
        line=dict(color='#EF5350', width=2, shape='spline'),
        marker=dict(size=6, color='#FF8A65', line=dict(color='#fff', width=1)),
        fill='tozeroy',
        fillcolor='rgba(239,83,80,0.10)',
        hovertemplate='Session %{x}<br>Risk: %{y:.2f}<extra></extra>',
    ))
    fig.update_layout(**_base_layout(
        height=300,
        xaxis_title='Session',
        yaxis_title='Risk (0=low, 1=critical)',
        yaxis=dict(range=[0, 1]),
    ))
    return fig


def create_weekly_chart(sentiments: list) -> go.Figure:
    """7-day mood chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=sentiments,
        mode='lines+markers',
        name='Daily Mood',
        line=dict(color='#4DD0E1', width=3, shape='spline'),
        marker=dict(size=7, color='#5B8CFF', line=dict(color='#fff', width=1)),
        fill='tozeroy',
        fillcolor='rgba(77,208,225,0.12)',
        hovertemplate='Day %{x}<br>Mood: %{y:.2f}<extra></extra>',
    ))
    fig.update_layout(**_base_layout(
        height=300,
        xaxis_title='Day', yaxis_title='Avg Mood',
    ))
    return fig


def create_sparkline(sentiments: list) -> go.Figure:
    """Tiny sentiment sparkline for the sidebar."""
    fig = go.Figure(go.Scatter(
        y=sentiments, mode='lines',
        line=dict(color='#5B8CFF', width=2),
        fill='tozeroy',
        fillcolor='rgba(91,140,255,0.10)',
    ))
    fig.update_layout(
        height=80,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=_TRANSPARENT,
        plot_bgcolor=_TRANSPARENT,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


# -----------------------------------------------------------------------
# Emotional journey charts
# -----------------------------------------------------------------------

def create_emotion_journey_line(emotion_timeline: list[dict]) -> go.Figure:
    """Create a session emotion-risk journey line from timeline entries."""
    if not emotion_timeline:
        emotion_timeline = [{'risk_score': 0.0, 'emotion': 'neutral'}]
    y_vals = [float(point.get('risk_score', 0.0)) for point in emotion_timeline]
    custom_emo = [point.get('emotion', 'neutral') for point in emotion_timeline]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=y_vals,
        mode='lines+markers',
        name='Emotion Journey',
        line=dict(color='#9B8CFF', width=3, shape='spline'),
        marker=dict(
            size=9,
            color=[EMO_COLORS.get(e, '#9B8CFF') for e in custom_emo],
            line=dict(color='#fff', width=1),
        ),
        fill='tozeroy',
        fillcolor='rgba(155,140,255,0.14)',
        customdata=custom_emo,
        hovertemplate='Turn %{x}<br>Risk: %{y:.2f}<br>Emotion: %{customdata}<extra></extra>',
    ))
    fig.update_layout(**_base_layout(
        height=300,
        xaxis_title='Conversation Turn',
        yaxis_title='Risk Intensity',
        yaxis=dict(range=[0, 1]),
        transition=dict(duration=_TRANSITION_DURATION, easing=_TRANSITION_EASING),
    ))
    return fig


def create_stress_intensity_gauge(risk_score: float) -> go.Figure:
    """Create wellness-oriented stress intensity gauge."""
    score = max(0.0, min(1.0, float(risk_score)))
    if score >= 0.75:
        tone = 'critical'
    elif score >= 0.50:
        tone = 'high'
    elif score >= 0.25:
        tone = 'medium'
    else:
        tone = 'low'
    fig = create_risk_gauge(score, tone)
    fig.update_layout(transition=dict(duration=_TRANSITION_DURATION, easing=_TRANSITION_EASING))
    fig.data[0].title['text'] = '<b>Stress Intensity</b>'
    return fig


# -----------------------------------------------------------------------
# Emotion heatmap
# -----------------------------------------------------------------------

_HEATMAP_EMOTIONS = ['joy', 'neutral', 'sadness', 'anger', 'fear', 'crisis']


def create_emotion_heatmap(emotion_timeline: list[dict]) -> go.Figure:
    """Create a Plotly heatmap showing emotional intensity over conversation time.

    Parameters
    ----------
    emotion_timeline : list[dict]
        List of dicts with keys matching emotion names and float intensity
        values (0–1).  Each dict represents one message/segment.
        Example: ``[{'joy': 0.8, 'sadness': 0.1, ...}, ...]``

    Returns a ``go.Figure`` ready for ``st.plotly_chart()``.
    """
    emotions = _HEATMAP_EMOTIONS
    z_data = []
    for emo in emotions:
        row = [seg.get(emo, 0.0) for seg in emotion_timeline]
        z_data.append(row)

    x_labels = [f'Msg {i+1}' for i in range(len(emotion_timeline))]

    fig = go.Figure(go.Heatmap(
        z=z_data,
        x=x_labels,
        y=[e.capitalize() for e in emotions],
        colorscale=[
            [0, 'rgba(240,244,255,0.8)'],
            [0.25, 'rgba(91,140,255,0.4)'],
            [0.5, 'rgba(155,140,255,0.6)'],
            [0.75, 'rgba(255,138,101,0.7)'],
            [1.0, 'rgba(239,83,80,0.9)'],
        ],
        hovertemplate='%{y}: %{z:.2f}<br>%{x}<extra></extra>',
        showscale=True,
        colorbar=dict(
            title=dict(text='Intensity', font=dict(size=11, family='Inter')),
            tickfont=dict(size=10, family='Inter'),
            len=0.8,
        ),
    ))
    fig.update_layout(**_base_layout(
        height=280,
        margin=dict(l=80, r=20, t=20, b=40),
        xaxis_title='Conversation Timeline',
    ))
    return fig
