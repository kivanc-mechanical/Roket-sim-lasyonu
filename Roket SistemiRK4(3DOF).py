import random
import json
import matplotlib.pyplot as plt
import math
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

print("-" * 57)
print("3B ROKET SİMÜLASYON TERMİNALİ v2.0 - RK4 MATRİSİ")
print("Hydra 70 Dinamik Kütle, Değişken Mach Cd ve Coriolis Aktif")
print("Bu kod kurgulanırken gözlemci ile mühimmat yöne bakacak şekilde kurgulanmıştır bir uçaktan yapılan atış gibi")
print("-" * 57)

try:
    # --- 1. ROKET VE MOTOR PARAMETRELERİ (HYDRA 70 Mk 66) ---

    roket_kutuphanesi={
        "Hydra_70_Mk66": {"kalibre_mm": 70.0,
                          "roket_boyu": 1.4,
                          "m_empty": 6.2,
                          "m_propellant_init": 4.0,
                          "v0": 40.0,
                          "thrust_force": 5800.0,
                          "burn_time": 1.1,
                          "yan_dragk": 1.2,
                          "damping_f": 0.002,          # İnce roket: Neredeyse hiç kafa sallama freni yemez
                          "induced_drag_k": 0.005       # İnce roket: Kanatçık girdap freni çok küçüktür
    }
    }

    try:
        with open("roketlerim.json", "r", encoding="utf-8") as f:
            roket_kutuphanesi.update(json.load(f))
            print(" Kayıtlı roket mühimmatları dosyadan başarıyla yüklendi.\n")
    except FileNotFoundError:
        print(" Kayıtlı roket dosyası bulunamadı, varsayılan askeri kütüphane yüklendi.\n")

    roket_secimi = input("\nLütfen simüle etmek istediğiniz roketi seçiniz veya yeni bir isim yazın: ").strip()

    if roket_secimi in roket_kutuphanesi:
        rocket_data = roket_kutuphanesi[roket_secimi]
        print(f" {roket_secimi} seçildi. Teknik veriler motor yükleniyor...")
    else:
        print(f" '{roket_secimi}' kütüphanede bulunamadı. Yeni roket tanımlama modülü başlatılıyor...")
        k_mm = float(input("1. Roket Kalibresi (mm): "))
        r_boy = float(input("2. Roket Gövde Boyu (metre): "))
        m_bos = float(input("3. Yakıtsız Boş Kütle (kg): "))
        m_yakit = float(input("4. Katı Yakıt Kütlesi (kg): "))
        ilk_hiz = float(input("5. Rampa Ayrılış/İlk Hızı (m/s): "))
        itki = float(input("6. Motor İtki Kuvveti (Newton): "))
        y_sure = float(input("7. Motor Yanma Süresi (Saniye): "))
        y_drag = float(input("8. Yanal Sürüklenme Katsayısı (Genelde 1.2): "))
        dam_f=float(input("9.üze burnunun hareketinden dolayı gerekli dumping katsayısı"))
        in_drag_k=float(input("10. kanatçıkların oluşturduğu girdap freni katsayısı"))


    # Yeni roketi sözlüğe ekle
        rocket_data = {
            "kalibre_mm": k_mm,
            "roket_boyu": r_boy,
            "m_empty": m_bos,
            "m_propellant_init": m_yakit,
            "v0": ilk_hiz,
            "thrust_force": itki,
            "burn_time": y_sure,
            "yan_dragk": y_drag,
            "damping_f":dam_f,
            "induced_drag_k":in_drag_k
        }
        roket_kutuphanesi[roket_secimi] = rocket_data

        # Dosyaya kalıcı olarak kaydet
        with open("roketlerim.json", "w", encoding="utf-8") as f:
            json.dump(roket_kutuphanesi, f, indent=4)
        print(f" '{roket_secimi}' başarıyla kütüphaneye eklendi ve roketlerim.json dosyasına kaydedildi!")

        # Seçilen roket verilerinin çözümlenmesi (Paketten çıkarma)
    kalibre_m = rocket_data["kalibre_mm"] / 1000.0
    roket_boyu = rocket_data["roket_boyu"]
    m_empty = rocket_data["m_empty"]  # Yakıtsız ağırlık (kg)
    m_propellant_init = rocket_data["m_propellant_init"] # İlk yakıt ağırlığı (kg)
    m_total = m_empty + m_propellant_init
    v0 = rocket_data["v0"]  # Rampa ayrılış hızı (m/s)
    thrust_force = rocket_data["thrust_force"] # Katı yakıt itkisi (Newton)
    burn_time = rocket_data["burn_time"]  ## Saniye
    yan_dragk = rocket_data["yan_dragk"]  #bu bir kabulleniş Silindirik cisimlerin yan drag katsayısı genelde 1.2 civarındadır
    
    mdot = m_propellant_init / burn_time  # Saniyede ~3.63 kg yakıt tüketir
    A_kesit = np.pi * (kalibre_m / 2)**2  # Ön kesit alanı (~0.00384 m^2)
    damping_f = rocket_data.get("damping_f", 0.005)
    induced_drag_k = rocket_data.get("induced_drag_k", 0.01)

                          
                    # --- 2. ÇEVRE VE BAŞLANGIÇ KOŞULLARI ---
    ######################################################################################
    pitch_deg = 0.0                 # Yatay düzlemle yapılan atış açısı (Pitch)                                                          
                                                                                        
    yaw_deg = 0.0                  # Atış pusula yönü (Yaw/Azimut - 0:Kuzey, 90:Doğu)   
    theta = np.radians(yaw_deg)                                                       
                                                                                        
    g0 = 9.80665                                                                         
    v_wind_y = 0.0                  # Yan rüzgar hızı (m/s)                            
    T = 22.0                        # Deniz seviyesi sıcaklık (C)                       
    P_basinc = 101325.0             # Deniz seviyesi basınç (Pa)                        
    N = 50.0                        # Bağıl nem (%)                                     
    atis_yuksekligi = 700.0         # Roketin fırlatıldığı rampa yüksekliği (m)           
    v_platform=180.0
    Cl_egimi = 1.8

    enlem_deg = 40     
    phi = np.radians(enlem_deg)                                                                        
    ######################################################################################

    # --- DÜNYA VE DÖNÜŞ PARAMETRELERİ (Coriolis) ---
    omega = 7.292115e-5  
    Re=6371000

        # LOGARİTMİK RÜZGAR İÇİN ARKA PLAN SABİTLERİ
    z_ref = 10.0                    # Standart askeri meteoroloji ölçüm yüksekliği (m)
    z0_pruzruzluk = 0.03            # Açık arazi / Poligon pürüzlülük sabiti (m)
    
    v_toplam_ilk = v0 + v_platform

    # Başlangıç Durum Vektörü [x, y, z, vx, vy, vz]
    radyan_aci=np.radians(pitch_deg)
    vx_ilk = v_toplam_ilk * math.cos(radyan_aci)
    vz_ilk = v_toplam_ilk * math.sin(radyan_aci)
    vy_ilk = v_wind_y

    state = np.array([0.0, 0.0, atis_yuksekligi, vx_ilk, vy_ilk, vz_ilk])

    # Simülasyon zaman parametreleri
    dt = 0.01            
    t = 0.0

    # Verileri kaydetmek için listeler
    x_hist, y_hist, z_hist = [state[0]], [state[1]], [state[2]]
    t_hist = [t]

    # --- 3. İVME FONKSİYONU (TÜREVSEL ÇEKİRDEK) ---
    def get_accelerations(state_vec, t_curr):
        x, y, z, vx, vy, vz = state_vec
        
        # Roket yere çarptıysa türevleri sıfırla
        if z < 0.0: return np.zeros(6)


        # [RÜZGAR PROFİLİ GRADİYENTİ]
        z_guvenli = max(z, z0_pruzruzluk + 0.1)
        v_wind_y_anlik = v_wind_y * (math.log(z_guvenli / z0_pruzruzluk) / math.log(z_ref / z0_pruzruzluk))

        # Bağıl hız hesaplamaları (Y ekseninde anlık rüzgar hızı düşülür)
        v_rel_x = vx
        v_rel_y = vy - v_wind_y_anlik 
        v_rel_z = vz
        v_rel_mag = np.sqrt(v_rel_x**2 + v_rel_y**2 + v_rel_z**2)
        if v_rel_mag == 0: v_rel_mag = 0.001
        
        # DOĞRU: İrtifaya (z) bağlı dinamik yerçekimi ivmesi
        g = g0 * (Re / (Re + z))**2

        # Nem Faktörlü Dinamik Atmosfer Modeli (ISA)
        T_kelvin = (T + 273.15) - (0.0065 * z)
        T_anlik_C = T - (0.0065 * z)
        P_anlik = 101325 * (1 - 0.000022557 * z)**5.2559
        psat = 6.1078 * 10**(7.5 * T_anlik_C / (T_anlik_C + 237.3))
        pv = psat * (N / 100) * 100 
        pd_anlik = P_anlik - pv
        rho = (pd_anlik / (287.05 * T_kelvin)) + (pv / (461.5 * T_kelvin))

        # Mach Sayısı Hesaplama
        v_ses = np.sqrt(1.4 * 287.05 * T_kelvin)   
        Mach = v_rel_mag / v_ses   
        
        # --- [1. ETAP] TEMEL CD HESABI ---
        if Mach < 0.8:
            Cd_anlik = 0.40  
        elif 0.8 <= Mach < 1.2:
            Cd_anlik = 0.40 + (Mach - 0.8) * 0.875
        elif 1.2 <= Mach < 2.0:
            Cd_anlik = 0.75 - (Mach - 1.2) * 0.25
        else:
            Cd_anlik = 0.55

        # --- [2. ETAP] GEOMETRİK NARİNLİK ÖLÇEKLİ DAMPING DRAG ---
        narinlik_orani = roket_boyu / kalibre_m 


        # DOĞRU YANAL RÜZGAR HESABI: Sabit v_wind_y değil, bağıl v_rel_y kullanılır!
        A_yan = kalibre_m * roket_boyu  
        # Roket rüzgar yönünde hızlandıkça v_rel_y küçülecek ve rüzgarın itme kuvveti azalacaktır
        F_yan_ruzgar = 0.5 * rho * (v_rel_y**2) * yan_dragk * A_yan
        # Kuvvet, bağıl hızın tersi yönünde etki eder (Rüzgar roketi sürükler)
        fy_wind_force = -F_yan_ruzgar * np.sign(v_rel_y) if v_rel_y != 0 else 0.0


        # --- [3. ETAP] KÜTLE VE İTKİ YÖNETİMİ ---
        if t_curr < burn_time:
            m_current = m_total - (mdot * t_curr)
            m_current = max(m_empty, m_current)
            
            # Üstel Sönümlenme (Tail-Off)
            solan_zaman = burn_time * 0.7  
            if t_curr > solan_zaman:
                lineer_oran = (burn_time - t_curr) / (burn_time - solan_zaman)
                carpan = lineer_oran ** 3
                anlik_itki = thrust_force * max(0.0, carpan)
            else:
                anlik_itki = thrust_force
             
            v_mag = np.sqrt(vx**2 + vy**2 + vz**2)
            if v_mag == 0: v_mag = 0.001
            
            tx = anlik_itki * (vx / v_mag)
            ty = anlik_itki * (vy / v_mag)
            tz = anlik_itki * (vz / v_mag)
            
            # [YENİ: COG SHIFT FACTOR] - Yakıt doluluk oranı (1.0'dan 0.0'a düşer)
            yakit_orani = (m_current - m_empty) / m_propellant_init
        else:
            tx = ty = tz = 0.0
            m_current = m_empty
            yakit_orani = 0.0  # Yakıt tamamen bitti, ağırlık merkezi en önde

        # Ağırlık merkezinin öne kaymasıyla kararlılık artar, sönümlenme katsayıları dinamikleşir
        # Yakıt bittikçe (yakit_orani -> 0), kafa sallama freni (damping) azalır, roket oklanır.
        damping_f_dinamik = damping_f * (0.5 + 0.5 * yakit_orani)
        induced_drag_k_dinamik = induced_drag_k * (0.4 + 0.6 * yakit_orani)

        # Sabit damping_f yerine dinamik olanı koyduk
        Cd_anlik += (damping_f_dinamik / narinlik_orani) * (Mach ** 2)


        # --- [4. ETAP] KÜTLESEL ÖLÇEKLİ INDUCED DRAG ---
        if v_rel_mag > 0:    
            kutle_faktoru = m_current / m_total
            # Sabit induced_drag_k yerine dinamik olanı koyduk
            Cd_anlik += (induced_drag_k_dinamik * kutle_faktoru) * (abs(vz) / v_rel_mag)

        # --- [YENİ VE GÜVENLİ: SAF TAŞIMA KUVVETİ (LIFT)] ---
        fx_lift = 0.0
        fz_lift = 0.0
        
        if t_curr > burn_time and v_rel_mag > 10.0:
            hareket_acisi_rad = np.arctan2(v_rel_z, np.sqrt(v_rel_x**2 + v_rel_y**2))
            alfa_rad = 0.04 * np.cos(hareket_acisi_rad)
            Cd_lift_orani = Cl_egimi * max(0.0, alfa_rad)
            F_lift = 0.5 * rho * (v_rel_mag**2) * Cd_lift_orani * A_kesit
            
            fx_lift = -F_lift * np.sin(abs(hareket_acisi_rad))
            fz_lift =  F_lift * np.cos(hareket_acisi_rad)
        
        # --- [5. ETAP] NİHAİ DRAG KUVVETİ HESABI ---
        F_drag = 0.5 * rho * (v_rel_mag**2) * Cd_anlik * A_kesit
        fx_drag = -F_drag * (v_rel_x / v_rel_mag)
        fy_drag = -F_drag * (v_rel_y / v_rel_mag)
        fz_drag = -F_drag * (v_rel_z / v_rel_mag)

        # Coriolis İvme Bileşenleri
        ax_cor = 2 * omega * (vy * math.cos(phi) * math.cos(theta) - vz * math.cos(phi) * math.sin(theta))
        ay_cor = 2 * omega * (vx * math.sin(phi) - vz * math.cos(phi) * math.cos(theta))
        az_cor = 2 * omega * vx * math.cos(phi) * math.sin(theta)

        # Toplam İvmeler (Rüzgar kuvveti doğrudan fy_wind_force ile yönetiliyor, fy_drag bağıl hızı dengeliyor)
        ax = ((tx + fx_drag + fx_lift) / m_current) + ax_cor
        ay = ((ty + fy_drag + fy_wind_force) / m_current) + ay_cor
        az = ((tz + fz_drag + fz_lift) / m_current) - g + az_cor

        return np.array([vx, vy, vz, ax, ay, az])

    # --- 4. RUNGE-KUTTA 4 (RK4) ANA DÖNGÜSÜ ---
    while state[2] >= 0.0:
        
        # RK4 Adımları
        k1 = get_accelerations(state, t)
        k2 = get_accelerations(state + k1 * dt / 2.0, t + dt / 2.0)
        k3 = get_accelerations(state + k2 * dt / 2.0, t + dt / 2.0)
        k4 = get_accelerations(state + k3 * dt, t + dt)

        # Durum Güncellemesi
        state = state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        
        # Zaman İlerlemesi
        t += dt

        # Geçmişi kaydet (Sadece roket havadaysa)
        if state[2] >= 0.0:
            x_hist.append(state[0])
            y_hist.append(state[1])
            z_hist.append(state[2])
            t_hist.append(t)
        
        # Güvenlik sınırı
        if t > 200: break

    # Anlık Pitch ve Yaw geometrisinin son duruş verisi
    v_yatay = np.sqrt(state[3]**2 + state[4]**2)
    if v_yatay == 0: v_yatay = 0.001
    anlik_pitch_deg = np.degrees(np.arctan2(state[5], v_yatay))

    # --- 5. GÖRSELLEŞTİRME VE RAPORLAMA ---
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(x_hist, y_hist, z_hist, label='Roket Yörüngesi (RK4)', color='crimson', linewidth=2.5)
    ax.scatter(0, 0, atis_yuksekligi, color='green', s=100, label='Fırlatma Rampası')

    burn_out_index = int(burn_time / dt)
    if burn_out_index < len(x_hist):
        ax.scatter(x_hist[burn_out_index], y_hist[burn_out_index], z_hist[burn_out_index], 
                   color='orange', s=100, marker='X', label='Motor Durma (Burnout)')
        
    print(f"--- RK4 ROKET ATIŞ VERİLERİ ---")
    print(f"Maksimum İrtifa (Apogee): {max(z_hist):.2f} metre")
    print(f"Toplam Uçuş Süresi: {t:.2f} saniye")
    print(f"Düşüş Menzili (X): {x_hist[-1]:.2f} metre")
    print(f"Rüzgar ve Coriolis Sapması (Y): {y_hist[-1]:.2f} metre")
    print(f"Yere Çakılma Pitch Açısı: {anlik_pitch_deg:.2f} derece")
 
    ax.set_title('RK4 Metodu ile 3B Değişken Kütleli Hydra 70 Roket Simülasyonu', fontsize=12)
    ax.set_xlabel('Menzil X (m)')
    ax.set_ylabel('Yan Sapma Y (m)')
    ax.set_zlabel('Yükseklik Z (m)')
    ax.set_zlim(0, max(z_hist) + 10)
    ax.view_init(elev=25, azim=-45)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    ax.invert_yaxis()
    plt.show()



except ValueError:
    print("Lütfen geçerli sayısal değerler giriniz.")

except Exception as e:
    print(f"\nSistemsel Hata: {e}")