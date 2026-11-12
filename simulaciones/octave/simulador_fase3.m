% =====================================================================
% ACE941 - FASE 3 | Verificacion en MATLAB / GNU Octave
% Circuito de la Fase 1 - Carlos Pena (Alternativa B)
% =====================================================================
clear; clc;

% 1. Parametros del circuito
Vs = 20;                        % Fuente independiente [V]
R1 = 2; R2 = 20; R3 = 5;        % Resistencias [Ohm]
R4 = 10; R5 = 2;
k  = 8;                         % Fuente dependiente VC = k*iphi [Ohm]

if any([R1 R2 R3 R4 R5] <= 0)
  error('Las resistencias deben ser mayores que 0 Ohm.');
end

% 2. Analisis nodal: G*V = I
G = [ 1/R1 + 1/R2 + 1/R3,    -1/R3;
     -1/R3 - (k/R3)/R5,       1/R3 + 1/R4 + 1/R5 + (k/R3)/R5 ];
I = [ Vs/R1; 0 ];

if rank(G) < size(G,1)
  error('Matriz de conductancias singular: sin solucion unica.');
end

V    = G \ I;
VA   = V(1);  VB = V(2);
iphi = (VA - VB) / R3;
VC   = k * iphi;

% 3. Analisis de mallas: Rm*im = E
Rm = [ R1+R2,   -R2,         0;
       -R2,      R2+R3+R4,  -R4;
        0,       k-R4,       R4+R5 ];
E  = [ Vs; 0; 0 ];
im = Rm \ E;

% 4. Corrientes de rama y potencias
iR1 = (Vs - VA) / R1;
iR2 = VA / R2;
iR4 = VB / R4;
iR5 = (VB - VC) / R5;

P_gen = Vs * iR1;
P     = [iR1^2*R1, iR2^2*R2, iphi^2*R3, iR4^2*R4, iR5^2*R5, VC*iR5];
P_abs = sum(P);

% 5. Resultados
fprintf('=== ANALISIS NODAL ===\n');
fprintf('VA = %.4f V | VB = %.4f V | VC = %.4f V\n', VA, VB, VC);
fprintf('iphi = %.4f A | P(5 Ohm) = %.4f W\n\n', iphi, P(3));

fprintf('=== VERIFICACION POR MALLAS ===\n');
fprintf('i1 = %.4f A | i2 = %.4f A | i3 = %.4f A\n\n', im(1), im(2), im(3));

fprintf('=== BALANCE DE POTENCIA ===\n');
fprintf('P generada  = %.4f W\n', P_gen);
fprintf('P absorbida = %.4f W  (R1 %.2f, R2 %.2f, R3 %.2f, R4 %.2f, R5 %.2f, Dep %.2f)\n\n', ...
        P_abs, P(1), P(2), P(3), P(4), P(5), P(6));

fprintf('=== DIAGNOSTICO NUMERICO ===\n');
fprintf('det(G) = %.4f | cond(G) = %.4f | residuo ||G*V - I|| = %.2e\n\n', ...
        det(G), cond(G), norm(G*V - I));

% 6. Comparacion con la teoria (Fase 1)
nombres  = {'VA (V)','VB (V)','VC (V)','iphi (A)','I R1 (A)', ...
            'I R2 (A)','I R4 (A)','I R5 (A)','P 5 Ohm (W)'};
teorico  = [16 10 9.6 1.2 2 0.8 1 0.2 7.2];
simulado = [VA VB VC iphi iR1 iR2 iR4 iR5 P(3)];
err_pct  = abs(teorico - simulado) ./ teorico * 100;

fprintf('=== COMPARACION TEORICO vs MATLAB/OCTAVE ===\n');
fprintf('%-12s %10s %12s %12s\n', 'Variable', 'Teorico', 'Octave', 'Error %');
for n = 1:numel(nombres)
  fprintf('%-12s %10.4f %12.6f %12.2e\n', nombres{n}, teorico(n), simulado(n), err_pct(n));
end