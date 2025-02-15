"""
Configuration for GPA mapping
Format of GPA mapping should be: bottom_range: float, top_range: float, gpa: float
"""

# taken from: https://www.google.com/url?sa=i&url=https%3A%2F%2Fwhs.wsdweb.org%2Facademics%2Fgrading&psig=AOvVaw2J_Qf0VfzK75xhDsH5Fyag&ust=1739730269384000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCIiplbimxosDFQAAAAAdAAAAABAE
# make gpa_mapping take a lower and upper range because I think it allows for any decimal place raw score to be mapped to a GPA
gpa_mapping = [
    (93, 100, 4.0),
    (90, 92, 3.7),
    (87, 89, 3.3),
    (83, 86, 3.0),
    (80, 82, 2.7),
    (77, 79, 2.3),
    (73, 76, 2.0),
    (70, 72, 1.7),
    (67, 69, 1.3),
    (65, 66, 1.0),
    (0, 64, 0.0),
]
