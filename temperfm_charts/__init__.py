import datetime
import svgwrite

__version__ = '0.1'


def _get_weekly_score_totals(report):
    """
    :type report: temperfm.records.UserWeeklyArtistReport
    :rtype: list[list[float]]
    """
    artist_scores = {artist_score.name: artist_score.scores for artist_score in report.artist_profile_scores}
    weekly_totals = []

    # Get total weekly scores
    for i, artist_plays in enumerate(report.artist_weekly):
        weekly_totals.append([0] * len(report.profile.clusters))
        for artist in artist_plays:
            scores = [x * artist.plays for x in artist_scores.get(artist.name, [])]
            for j in range(max(len(report.profile.clusters), len(scores))):
                weekly_totals[i][j] += scores[j]

    return weekly_totals


def _get_weekly_total_plays(report):
    """
    :type report: temperfm.records.UserWeeklyArtistReport
    :rtype: list[int]
    """
    weekly_totals = []

    # Get total weekly plays
    for artist_plays in report.artist_weekly:
        weekly_totals.append(sum([artist.plays for artist in artist_plays]))

    return weekly_totals


def _color_to_css(color):
    """
    :type color: tuple[float, float, float]
    :rtype: str
    """
    return 'rgb({})'.format(', '.join([str(int(x * 255)) for x in color]))


def _draw_text(dwg, text, position, color, size=12, rotation=-0.5):
    """
    :type dwg: svgwrite.Drawing
    :type text: str
    :type position: tuple[int | float, int | float]
    :type color: tuple[float, float, float]
    :type size: int
    :type rotation: float
    """
    elm = dwg.text(text, font_family='sans-serif', font_size=size, text_anchor='end', fill=_color_to_css(color))
    elm.translate(*position)
    elm.rotate(rotation * (180 / 3.14159))
    dwg.add(elm)


def _get_monotonic_spline_commands(points):
    """
    :type points: list[tuple[float, float]]
    :rtype: list[str]
    """
    if len(points) < 3:
        return [f'L{x},{y}' for x, y in points[1:]]

    from .splines import get_monotonic_spline_tangents

    tangents = get_monotonic_spline_tangents(points)

    assert len(points) == len(tangents)

    commands = [
        f'C{points[0][0] + tangents[0][0]},{points[0][1] + tangents[0][1]},'
        f'{points[1][0] - tangents[1][0]},{points[1][1] - tangents[0][1]},'
        f'{points[1][0]},{points[1][1]}'
    ]

    for i in range(2, len(tangents)):
        point = points[i]
        tangent = tangents[i]
        commands.append(f'S{point[0] - tangent[0]},{point[1] - tangent[1]},{point[0]},{point[1]}')

    return commands


def render_user_weekly_artists(report, file_path, size=(420, 300)):
    """
    :type report: temperfm.records.UserWeeklyArtistReport
    :type file_path: str
    :type size: tuple[int, int]
    """
    margin_size = 60, 35
    graph_size = size[0] - margin_size[0], size[1] - margin_size[1]
    graph_border = 2
    font_size = 12

    weekly_scores = _get_weekly_score_totals(report)
    weekly_plays = _get_weekly_total_plays(report)
    weekly_plays_max = max(weekly_plays)

    graph_week_span = graph_size[0] / (len(weekly_scores) - 1)

    # Normalize and sanitize scores
    for i, week_scores in enumerate(weekly_scores):
        score_sum = sum(week_scores)

        # Sanitize zero sum week scores
        j = i
        while score_sum == 0:
            if i == 0:
                score_sum = len(week_scores)
                week_scores = [1] * score_sum
            else:
                j -= 1
                week_scores = weekly_scores[j]
                score_sum = sum(week_scores)

        # Normalize
        weekly_scores[i] = [score / score_sum for score in week_scores]

    # Build cluster paths
    cluster_positions = []
    last_scores = [0] * len(weekly_scores)
    for i in range(len(report.profile.clusters) - 1):
        scores = [week_scores[i] for week_scores in weekly_scores]
        scores = [scores[j] + last_scores[j] for j in range(len(scores))]
        cluster_positions.append([score * graph_size[1] for score in scores])
        last_scores = scores
    cluster_positions.append([graph_size[1]] * len(weekly_scores))

    # Begin drawing
    dwg = svgwrite.Drawing(file_path, size=size)

    graph_clip = dwg.clipPath(id='graph_clip')
    graph_clip.add(dwg.rect((0, 0), graph_size))
    dwg.defs.add(graph_clip)

    graph = dwg.g(clip_path='url(#graph_clip)')
    graph.translate(margin_size[0] + graph_border)
    dwg.add(graph)

    # Cluster fill
    points_prev = [(0, 0), (graph_size[0], 0)]
    for i, positions in enumerate(cluster_positions):
        cluster = report.profile.clusters[i]
        x_span = graph_size[0] / (len(positions) - 1)
        points = [(x * x_span, y) for x, y in enumerate(positions)]

        commands = [f'M0,{points[0][1]}'] + \
                   _get_monotonic_spline_commands(points) + \
                   [f'L{graph_size[0]},{points_prev[-1][1]}'] + \
                   _get_monotonic_spline_commands(list(reversed(points_prev)))
        graph.add(dwg.path(commands, fill=_color_to_css(cluster.color)))

        points_prev = points

    # # Play counts
    for i in range(len(weekly_plays)):
        width = int(graph_week_span) - 4
        height = int((weekly_plays[i] / weekly_plays_max) * graph_size[1] * 0.9)
        x = int(((graph_week_span * i) - (graph_week_span / 2))) + 2
        y = int((graph_size[1] / 2) - (height / 2))
        graph.add(dwg.rect((x, y), (width, height), fill=_color_to_css((0.94, 0.94, 0.94)), fill_opacity=0.14))

    # Cluster stroke
    for i, positions in enumerate(cluster_positions[:-1]):
        x_span = graph_size[0] / (len(positions) - 1)
        points = [(x * x_span, y) for x, y in enumerate(positions)]

        commands = [f'M0,{points[0][1]}'] + _get_monotonic_spline_commands(points)
        graph.add(dwg.path(commands, stroke=_color_to_css((255, 255, 255)), stroke_width=1, fill_opacity=0))

    # # Cluster labels
    last_y = 0
    for i, cluster in enumerate(report.profile.clusters):
        y = cluster_positions[i][0]
        if i > 0:
            y += cluster_positions[i - 1][0]
        y = max((last_y + font_size, y / 2))
        last_y = y

        _draw_text(dwg, cluster.name, (margin_size[0], y), cluster.color, size=font_size)

    # Modulo to skip every n week date labels. 1 + floor(1 / (available space / required space))
    skip_mod = 1 + int(1 / ((graph_size[0] / (font_size * (len(report.artist_weekly)))) / (font_size * 0.175)))

    # Week date labels
    for i in range(len(report.artist_weekly)):
        if (len(report.artist_weekly) - i - 1) % skip_mod != 0:
            continue

        date = min((report.start_date + datetime.timedelta(days=(i * 7) + 6), datetime.date.today()))
        date_str = date.strftime('%b-%d')

        _draw_text(dwg, date_str, ((graph_week_span * i) + margin_size[0], graph_size[1] + font_size - graph_border),
                   (0.21, 0.21, 0.21), size=font_size)

    dwg.save()
