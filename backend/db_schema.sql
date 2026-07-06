-- ============================================================
-- Material Selection Optimizer - Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS material_optimizer;
USE material_optimizer;

DROP TABLE IF EXISTS materials;

CREATE TABLE materials (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    name                    VARCHAR(100) NOT NULL,
    category                VARCHAR(50)  NOT NULL,          -- Ferrous, Non-Ferrous, Polymer, Composite, Ceramic
    density                 FLOAT NOT NULL,                 -- kg/m3
    yield_strength          FLOAT NOT NULL,                 -- MPa
    ultimate_tensile_strength FLOAT NOT NULL,                -- MPa
    youngs_modulus          FLOAT NOT NULL,                 -- GPa
    cost_per_kg             FLOAT NOT NULL,                 -- INR/kg (approx market rate)
    thermal_conductivity    FLOAT NOT NULL,                 -- W/m.K
    corrosion_resistance    INT   NOT NULL,                 -- rating 1 (poor) - 10 (excellent)
    melting_point           FLOAT NOT NULL,                 -- deg C
    hardness_bhn            FLOAT NOT NULL                  -- Brinell Hardness Number (approx equivalent used across categories)
);

INSERT INTO materials
(name, category, density, yield_strength, ultimate_tensile_strength, youngs_modulus, cost_per_kg, thermal_conductivity, corrosion_resistance, melting_point, hardness_bhn)
VALUES
('Mild Steel (AISI 1018)',        'Ferrous',     7870, 370,  440,  205, 55,   51.9, 3,  1450, 126),
('Structural Steel (ASTM A36)',   'Ferrous',     7850, 250,  400,  200, 50,   50.0, 3,  1425, 119),
('Stainless Steel 304',           'Ferrous',     8000, 215,  505,  193, 220,  16.2, 8,  1400, 201),
('Stainless Steel 316',           'Ferrous',     8000, 205,  515,  193, 260,  16.3, 9,  1375, 217),
('Tool Steel D2',                 'Ferrous',     7700, 1500, 1900, 210, 480,  20.0, 5,  1421, 550),
('Cast Iron (Grey CI)',           'Ferrous',     7200, 130,  200,  110, 45,   52.0, 3,  1200, 180),
('Aluminium 6061-T6',             'Non-Ferrous', 2700, 276,  310,  68.9, 260,  167.0, 6,  652,  95),
('Aluminium 7075-T6',             'Non-Ferrous', 2810, 503,  572,  71.7, 340,  130.0, 4,  635,  150),
('Titanium Grade 5 (Ti-6Al-4V)',  'Non-Ferrous', 4430, 880,  950,  113.8, 3200, 6.7,  10, 1660, 334),
('Copper C11000',                 'Non-Ferrous', 8960, 69,   220,  110, 700,  391.0, 7,  1085, 40),
('Brass (C36000)',                'Non-Ferrous', 8500, 124,  338,  97,  480,  115.0, 6,  930,  78),
('Magnesium AZ31B',                'Non-Ferrous', 1770, 200,  260,  45,  480,  96.0,  3,  630,  49),
('Nickel Alloy Inconel 625',      'Non-Ferrous', 8440, 460,  930,  208, 3500, 9.8,  10, 1350, 220),
('ABS Plastic',                   'Polymer',     1050, 40,   45,   2.3, 180,  0.17, 8,  105,  8),
('Nylon 6/6 (PA66)',              'Polymer',     1140, 55,   82,   2.9, 220,  0.25, 8,  260,  10),
('Polycarbonate (PC)',            'Polymer',     1200, 62,   67,   2.4, 260,  0.20, 8,  267,  10),
('HDPE',                          'Polymer',     955,  26,   30,   1.0, 110,  0.48, 9,  130,  6),
('PTFE (Teflon)',                 'Polymer',     2200, 15,   25,   0.5, 620,  0.25, 10, 327,  5),
('Epoxy (unfilled)',              'Polymer',     1150, 60,   75,   3.0, 350,  0.20, 8,  150,  10),
('Carbon Fiber Reinforced Polymer (CFRP)', 'Composite', 1600, 600, 700, 135, 3800, 5.0, 10, 300, 250),
('Glass Fiber Reinforced Polymer (GFRP)', 'Composite', 1900, 200, 350, 25,  650,  0.4,  9,  200, 100),
('Kevlar Composite',              'Composite',   1440, 550,  620,  83,  4200, 0.04, 10, 500,  200),
('Alumina (Al2O3)',               'Ceramic',     3950, 0,    300,  380, 900,  30.0, 10, 2072, 1500),
('Silicon Carbide (SiC)',         'Ceramic',     3210, 0,    550,  410, 1500, 120.0, 10, 2730, 2500),
('Zirconia (ZrO2)',               'Ceramic',     6000, 0,    500,  200, 2200, 2.0,  10, 2715, 1200),
('Tungsten Carbide (WC-Co)',      'Ceramic',     15600, 0,   400,  600, 4500, 84.0, 9,  2870, 1800);
