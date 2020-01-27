
def sourceAnalysis(frequency_of_event, duration_of_event, total_sub_area, urban_area_future, green_area_future):
    c = 127.6537
    alpha = -0.75764
    probability = 1/frequency_of_event

    expected_rainfall_intensity = c * (duration_of_event ^ alpha)
    total_design_rainfall_for_analysis = duration_of_event * expected_rainfall_intensity

    total_urban_area = urban_area_future/(100 * total_sub_area * 1000000)
    urban_area_minus_urban_greenspace = total_urban_area - green_portion_urban_areas
    green_portion_urban_areas = green_area_future/100 * urban_area_minus_urban_greenspace/100 * total_sub_area * 1000000
    rural_area = (100 - urban_area_future)/100*total_sub_area*1000000
    urban_runoff_potential =


def pathwaysAnalysis(gamblings_polders, storageaddedwithcanals, lakes_wetlands_parks, greenways_canals_parks):





def main():


if __name__ == '__main__':
