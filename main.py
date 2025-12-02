# app.py
import streamlit as st
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import time

# 固定后端，防止渲染冲突
matplotlib.use("Agg")
plt.rcParams['animation.embed_limit'] = 2**128

st.set_page_config(page_title="交互式物理实验模拟器", layout="centered")
st.title("交互式物理实验模拟器（原生动画版）")

tab1, tab2, tab3 = st.tabs(["自由落体", "单摆周期测量", "斜面运动"])

# ================= 1. 自由落体 =================
with tab1:
    st.header("自由落体实验")
    initial_height = st.number_input("初始高度 (m)", 1.0, 100.0, 10.0, key="fall_h")
    g = st.number_input("重力加速度 (m/s²)", 9.0, 10.0, 9.8, key="fall_g")

    t_total = np.sqrt(2 * initial_height / g)
    t = np.linspace(0, t_total, 100)
    h = initial_height - 0.5 * g * t**2
    v = g * t

    # ---- 动画 ----
    fall_place = st.empty()
    if st.button("▶ 开始自由落体动画", key="btn_fall"):
        for frame in range(len(t)):
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.set_xlim(-1, 1)
            ax.set_ylim(0, initial_height + 1)
            ax.set_xlabel("水平位置")
            ax.set_ylabel("高度 (m)")
            ax.set_title(f"自由落体运动（t={t[frame]:.2f}s）")
            ax.axhline(y=0, color='black', linewidth=2, label="地面")
            ax.plot([0], [h[frame]], 'ro', markersize=10, label="下落物体")
            ax.legend()
            plt.tight_layout()
            fall_place.pyplot(fig)
            plt.close(fig)
            time.sleep(0.05)
        fall_place.success("动画播放完毕")

    # ---- 静态图表 ----
    st.subheader("运动曲线")
    fig_static, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.plot(t, h, 'blue')
    ax1.set(xlabel='时间 (s)', ylabel='高度 (m)', title='高度变化')
    ax1.grid(True)
    ax2.plot(t, v, 'red')
    ax2.set(xlabel='时间 (s)', ylabel='速度 (m/s)', title='速度变化')
    ax2.grid(True)
    st.pyplot(fig_static)

    # ---- 数据导出 ----
    data = pd.DataFrame({'时间 (s)': t, '高度 (m)': h, '速度 (m/s)': v})
    st.dataframe(data)
    st.download_button("导出CSV", data.to_csv(index=False).encode('utf-8'),
                       file_name="自由落体数据.csv", mime='text/csv')

# ================= 2. 单摆 =================
with tab2:
    st.header("单摆周期测量实验")
    length = st.number_input("摆长 (m)", 0.1, 2.0, 1.0, key="pendulum_l")
    theta0 = st.number_input("初始摆角 (°)", 1, 30, 5, key="pendulum_theta")
    theta0_rad = np.radians(theta0)
    g_pendulum = 9.8
    T_theory = 2 * np.pi * np.sqrt(length / g_pendulum)
    t_pendulum = np.linspace(0, 2 * T_theory, 200)
    theta = theta0_rad * np.cos(np.sqrt(g_pendulum / length) * t_pendulum)

    # ---- 动画 ----
    pend_place = st.empty()
    if st.button("▶ 开始单摆动画", key="btn_pend"):
        for frame in range(len(t_pendulum)):
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.set_xlim(-length - 0.5, length + 0.5)
            ax.set_ylim(-length - 0.5, 0.5)
            ax.set(xlabel="水平位置 (m)", ylabel="垂直位置 (m)", title="单摆运动动画")
            ax.plot([0], [0], 'ko', markersize=8, label="悬点")
            x = length * np.sin(theta[frame])
            y = -length * np.cos(theta[frame])
            ax.plot([0, x], [0, y], 'b-', linewidth=2)
            ax.plot([x], [y], 'ro', markersize=12, label="摆球")
            ax.legend()
            ax.grid(True)
            plt.tight_layout()
            pend_place.pyplot(fig)
            plt.close(fig)
            time.sleep(0.03)
        pend_place.success("动画播放完毕")

    # ---- 周期计算 ----
    peaks_idx = np.where(np.diff(np.sign(np.diff(np.degrees(theta)))) < 0)[0] + 1
    T_fit = t_pendulum[peaks_idx[1]] - t_pendulum[peaks_idx[0]] if len(peaks_idx) >= 2 else T_theory
    st.info(f"理论周期：{T_theory:.4f} s | 拟合周期：{T_fit:.4f} s")

    # ---- 静态图表 ----
    fig_static, ax = plt.subplots(figsize=(8, 4))
    ax.plot(t_pendulum, np.degrees(theta), 'purple')
    ax.set(xlabel='时间 (s)', ylabel='摆角 (°)', title='摆角变化')
    ax.grid(True)
    st.pyplot(fig_static)

    # ---- 数据导出 ----
    data_pend = pd.DataFrame({'时间 (s)': t_pendulum, '摆角 (°)': np.degrees(theta)})
    st.dataframe(data_pend)
    st.download_button("导出CSV", data_pend.to_csv(index=False).encode('utf-8'),
                       file_name="单摆数据.csv", mime='text/csv')

# ================= 3. 斜面运动 =================
with tab3:
    st.header("斜面运动实验")
    theta_incline = st.number_input("斜面倾角 (°)", 1, 80, 30, key="incline_theta")
    mu = st.number_input("摩擦系数 (μ)", 0.0, 1.0, 0.1, key="incline_mu")
    initial_velocity = st.number_input("初始速度 (m/s)", 0.0, 5.0, 0.0, key="incline_v0")
    incline_length = st.number_input("斜面长度 (m)", 1.0, 10.0, 2.0, key="incline_L")
    g_incline = 9.8
    a = g_incline * (np.sin(np.radians(theta_incline)) - mu * np.cos(np.radians(theta_incline)))

    if a <= 0:
        st.warning("加速度≤0，物体无法下滑！请减小摩擦系数或增大倾角。")
    else:
        t_incline_total = np.roots([0.5 * a, initial_velocity, -incline_length])[1]
        t_incline = np.linspace(0, t_incline_total, 100)
        s = initial_velocity * t_incline + 0.5 * a * t_incline**2

        # ---- 动画 ----
        incline_place = st.empty()
        if st.button("▶ 开始斜面动画", key="btn_incline"):
            for frame in range(len(t_incline)):
                fig, ax = plt.subplots(figsize=(8, 4))
                incline_x = [0, incline_length * np.cos(np.radians(theta_incline))]
                incline_y = [0, incline_length * np.sin(np.radians(theta_incline))]
                ax.plot(incline_x, incline_y, 'k-', linewidth=3, label="斜面")
                x = s[frame] * np.cos(np.radians(theta_incline))
                y = s[frame] * np.sin(np.radians(theta_incline))
                ax.plot([x], [y], 'ro', markersize=10, label="运动物体")
                ax.set(xlim=(-0.5, incline_x[1] + 0.5), ylim=(-0.5, incline_y[1] + 0.5),
                       xlabel="水平位置 (m)", ylabel="垂直位置 (m)", title="斜面运动动画")
                ax.legend()
                ax.grid(True)
                plt.tight_layout()
                incline_place.pyplot(fig)
                plt.close(fig)
                time.sleep(0.05)
            incline_place.success("动画播放完毕")

        # ---- 静态图表 ----
        st.subheader("运动曲线")
        fig_static, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        ax1.plot(t_incline, s, 'green')
        ax1.set(xlabel='时间 (s)', ylabel='位移 (m)', title='位移变化')
        ax1.grid(True)
        v_incline = initial_velocity + a * t_incline
        ax2.plot(t_incline, v_incline, 'orange')
        ax2.set(xlabel='时间 (s)', ylabel='速度 (m/s)', title='速度变化')
        ax2.grid(True)
        st.pyplot(fig_static)

        # ---- 数据导出 ----
        data_incline = pd.DataFrame({'时间 (s)': t_incline,
                                     '位移 (m)': s,
                                     '速度 (m/s)': v_incline})
        st.dataframe(data_incline)
        st.download_button("导出CSV", data_incline.to_csv(index=False).encode('utf-8'),
                           file_name="斜面运动数据.csv", mime='text/csv')