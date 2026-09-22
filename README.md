# 🚀 3B Roket Simülasyon Terminali (RK4 Matrisi)

Bu proje; 3 serbestlik dereceli (3DOF), değişken kütleli, aerodinamik ve çevresel faktörleri dikkate alan yüksek hassasiyetli bir roket yörünge simülasyonudur. Simülasyon çekirdeği **4. Dereceden Runge-Kutta (RK4)** nümerik entegrasyon yöntemini kullanır.

Sistem; Hydra 70 Mk 66 roket geometrisi varsayılan olarak tanımlı halde gelir, bunun yanında kullanıcıların özel mühimmat/roket parametrelerini girip yerel kütüphaneye (`roketlerim.json`) kaydetmelerine ve simüle etmelerine olanak tanır.

---

## ✨ Öne Çıkan Özellikler

* **4. Dereceden Runge-Kutta (RK4) Entegratörü:** Fiziksel türevsel denklem matrisini zamana bağlı olarak yüksek hassasiyetle çözer.
* **Dinamik Kütle & İtki Yönetimi:** Motor yanma süresince yakıt tüketimine (`mdot`) bağlı olarak kütle azalır. Motor kapanışına doğru *Tail-Off* (üstel sönümlenme) modellenmiştir.
* **Gelişmiş Atmosfer Modeli (ISA & Nem):** İrtifaya bağlı olarak sıcaklık, basınç, bağıl nem ve hava yoğunluğu (`rho`) dinamik olarak hesaplanır.
* **Gelişmiş Aerodinamik & Sürüklenme (Drag):**
  * **Mach Sayısına Bağlı $C_d$:** Ses altı, transonik ve ses üstü rejimler için dinamik sürüklenme katsayısı.
  * **Damping & Induced Drag:** Ağırlık merkezinin kayması (CoG Shift) ve geometrik narinlik oranına göre dinamikleşen sönümlenme ve indüklenmiş sürüklenme.
  * **Taşıma Kuvveti (Lift):** Yanma sonrası hücum açısına bağlı pasif taşıma kuvveti modülü.
* **Çevre ve Gezegensel Etkiler:**
  * **Coriolis İvmesi:** Enlem ve atış yönüne (Yaw/Pitch) bağlı Dünya dönüş etkisi.
  * **Logaritmik Rüzgar Profili:** İrtifa arttıkça değişen rüzgar hızı gradyanı ve bağıl rüzgar kuvveti.
  * **Dinamik Yerçekimi:** İrtifaya ($z$) bağlı değişen yerçekimi ivmesi.
* **Görselleştirme & Veri Yönetimi:** Matplotlib 3B grafik çizimi ve JSON tabanlı roket kütüphanesi desteği.

---

## 🛠️ Gereksinimler

Projenin çalışabilmesi için sisteminizde Python 3.x ve aşağıdaki kütüphanelerin yüklü olması gerekir:

```bash
pip install numpy matplotlib
