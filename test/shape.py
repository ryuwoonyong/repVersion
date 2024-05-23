import matplotlib.pyplot as plt

def draw_shapes_with_color(circle_color, rectangle_color):
    """
    주어진 색상으로 원과 사각형을 그리는 함수
    """
    # 그림과 축 설정
    fig, ax = plt.subplots()

    # 원 그리기
    circle = plt.Circle((0.5, 0.5), 0.2, color=circle_color)
    ax.add_patch(circle)

    # 사각형 그리기
    rectangle = plt.Rectangle((0.1, 0.1), 0.3, 0.2, color=rectangle_color)
    ax.add_patch(rectangle)

    # 축 설정
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal', adjustable='box')

    # 그래프 표시
    plt.show()

# 색상을 입력 받아서 도형을 그리기
#circle_color = input("Enter the color for the circle (e.g., 'red', 'blue', '#00FF00'): ")
#rectangle_color = input("Enter the color for the rectangle (e.g., 'red', 'blue', '#00FF00'): ")

draw_shapes_with_color('red', 'blue')