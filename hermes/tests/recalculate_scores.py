from .models import TestResult
from .score_tables import (
    calculate_beep_test_total_laps,
    calculate_score,
    calculate_y_test_index,
)


from django.contrib import messages
from django.shortcuts import redirect


def recalculate_scores(request):
    # Get all TestResult objects
    test_results = TestResult.objects.all()

    # Recalculate scores for each test result
    for test_result in test_results:
        # Recalculate ladder score
        if test_result.ladder_time_1 and test_result.ladder_time_2:
            age = test_result.profile.age
            gender = test_result.profile.gender
            time_1 = test_result.ladder_time_1
            time_2 = test_result.ladder_time_2
            test_result.ladder_score = calculate_score(
                age, gender, "ladder", time_1, time_2
            )

        # Recalculate brace score
        if test_result.brace_time_1 and test_result.brace_time_2:
            age = test_result.profile.age
            gender = test_result.profile.gender
            time_1 = test_result.brace_time_1
            time_2 = test_result.brace_time_2
            test_result.brace_score = calculate_score(
                age, gender, "brace", time_1, time_2
            )

        # Recalculate hexagon score
        if test_result.hexagon_time_cw and test_result.hexagon_time_ccw:
            age = test_result.profile.age
            gender = test_result.profile.gender
            time_cw = test_result.hexagon_time_cw
            time_ccw = test_result.hexagon_time_ccw
            test_result.hexagon_score = calculate_score(
                age, gender, "hexagon", time_cw, time_ccw
            )

        # Recalculate medicimbal score
        if (
            test_result.medicimbal_throw_1
            and test_result.medicimbal_throw_2
            and test_result.medicimbal_throw_3
        ):
            age = test_result.profile.age
            gender = test_result.profile.gender
            throw_1 = test_result.medicimbal_throw_1
            throw_2 = test_result.medicimbal_throw_2
            throw_3 = test_result.medicimbal_throw_3
            test_result.medicimbal_score = calculate_score(
                age, gender, "medicimbal", throw_1, throw_2, throw_3
            )

        # Recalculate jet score
        if test_result.jet_laps and test_result.jet_sides:
            age = test_result.profile.age
            gender = test_result.profile.gender
            laps = test_result.jet_laps
            sides = test_result.jet_sides
            jet_distance = laps * 40 + sides * 10
            test_result.jet_score = calculate_score(age, gender, "jet", jet_distance)
            test_result.jet_distance = jet_distance

        # Recalculate y-test score and index
        if (
            test_result.y_test_ll_front
            and test_result.y_test_ll_left
            and test_result.y_test_ll_right
            and test_result.y_test_rl_front
            and test_result.y_test_rl_right
            and test_result.y_test_rl_left
            and test_result.y_test_la_left
            and test_result.y_test_la_front
            and test_result.y_test_la_back
            and test_result.y_test_ra_right
            and test_result.y_test_ra_front
            and test_result.y_test_ra_back
        ):
            age = test_result.profile.age
            gender = test_result.profile.gender
            height = test_result.profile.height
            ll_front = test_result.y_test_ll_front
            ll_left = test_result.y_test_ll_left
            ll_right = test_result.y_test_ll_right
            rl_front = test_result.y_test_rl_front
            rl_right = test_result.y_test_rl_right
            rl_left = test_result.y_test_rl_left
            la_left = test_result.y_test_la_left
            la_front = test_result.y_test_la_front
            la_back = test_result.y_test_la_back
            ra_right = test_result.y_test_ra_right
            ra_front = test_result.y_test_ra_front
            ra_back = test_result.y_test_ra_back

            test_result.y_test_score = calculate_score(
                age,
                gender,
                "y_test",
                height,
                ll_front,
                ll_left,
                ll_right,
                rl_front,
                rl_right,
                rl_left,
                la_left,
                la_front,
                la_back,
                ra_right,
                ra_front,
                ra_back,
            )
            test_result.y_test_index = calculate_y_test_index(
                height,
                ll_front,
                ll_left,
                ll_right,
                rl_front,
                rl_right,
                rl_left,
                la_left,
                la_front,
                la_back,
                ra_right,
                ra_front,
                ra_back,
            )

        # Recalculate beep test score
        if test_result.beep_test_laps and test_result.beep_test_level:
            age = test_result.profile.age
            gender = test_result.profile.gender
            laps = test_result.beep_test_laps
            level = test_result.beep_test_level
            total_laps = calculate_beep_test_total_laps(level, laps)
            test_result.beep_test_score = calculate_score(
                age, gender, "beep_test", total_laps
            )
            test_result.beep_test_total_laps = total_laps

        # Recalculate triple jump score
        if (
            test_result.triple_jump_distance_1
            and test_result.triple_jump_distance_2
            and test_result.triple_jump_distance_3
        ):
            age = test_result.profile.age
            gender = test_result.profile.gender
            jump_1 = test_result.triple_jump_distance_1
            jump_2 = test_result.triple_jump_distance_2
            jump_3 = test_result.triple_jump_distance_3
            test_result.triple_jump_score = calculate_score(
                age, gender, "triple_jump", jump_1, jump_2, jump_3
            )

        # Save the updated test result
        test_result.save()

    messages.success(request, "Scores recalculated successfully!")
    return redirect("results")

