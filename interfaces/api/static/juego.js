// Juego de Alineaciones Históricas de la Universidad de Chile

let selectedMode = 'normal';
let selectedFormation = '4-4-2';
let activeSlotIndex = null;
let dreamTeam = Array(11).fill(null);
let draftProgress = 0;
let teamRating = 0.0;

// Variables de Ruleta y Draft
let resortCount = 2;
let currentSorteadoPlantel = null;
let selectedPlayerToPlace = null; // Jugador seleccionado de la lista esperando ser ubicado
let rouletteInterval = null;
let isSpinning = false;
let availablePlantelKeys = [];

// Datos de torneo
let teamName = "";
let tournamentStage = "groups"; // "groups", "octavos", "cuartos", "semis", "final", "winner", "gameover"
let currentMatchIndex = 0; // Para el fixture de grupos (0, 1, 2)
let tournamentTeams = []; // Array de los 32 equipos
let groupStandings = []; // Los 4 equipos del grupo del usuario
let playoffOpponent = null;
let playoffStageIndex = 0; // 0=Octavos, 1=Cuartos, 2=Semis, 3=Final
const playoffStageNames = ["Octavos de Final", "Cuartos de Final", "Semifinal", "Gran Final"];

// Estructura de posiciones para cada formación
const FORMACIONES = {
    '4-4-2': [
        { id: 0, pos: 'ARQ', label: 'ARQ', row: 1 },
        { id: 4, pos: 'DEF', label: 'LI', row: 2 },
        { id: 2, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 3, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 1, pos: 'DEF', label: 'LD', row: 2 },
        { id: 8, pos: 'MED', label: 'MI', row: 3 },
        { id: 5, pos: 'MED', label: 'MC', row: 3 },
        { id: 6, pos: 'MED', label: 'MC', row: 3 },
        { id: 7, pos: 'MED', label: 'MD', row: 3 },
        { id: 9, pos: 'DEL', label: 'DC', row: 4 },
        { id: 10, pos: 'DEL', label: 'DC', row: 4 }
    ],
    '4-3-3': [
        { id: 0, pos: 'ARQ', label: 'ARQ', row: 1 },
        { id: 4, pos: 'DEF', label: 'LI', row: 2 },
        { id: 2, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 3, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 1, pos: 'DEF', label: 'LD', row: 2 },
        { id: 5, pos: 'MED', label: 'MC', row: 3 },
        { id: 6, pos: 'MED', label: 'MC', row: 3 },
        { id: 7, pos: 'MED', label: 'MCO', row: 3 },
        { id: 10, pos: 'DEL', label: 'EI', row: 4 },
        { id: 9, pos: 'DEL', label: 'DC', row: 4 },
        { id: 8, pos: 'DEL', label: 'ED', row: 4 }
    ],
    '3-5-2': [
        { id: 0, pos: 'ARQ', label: 'ARQ', row: 1 },
        { id: 1, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 2, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 3, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 8, pos: 'MED', label: 'MI', row: 3 },
        { id: 4, pos: 'MED', label: 'MCD', row: 3 },
        { id: 5, pos: 'MED', label: 'MC', row: 3 },
        { id: 6, pos: 'MED', label: 'MC', row: 3 },
        { id: 7, pos: 'MED', label: 'MD', row: 3 },
        { id: 9, pos: 'DEL', label: 'DC', row: 4 },
        { id: 10, pos: 'DEL', label: 'DC', row: 4 }
    ],
    '4-2-3-1': [
        { id: 0, pos: 'ARQ', label: 'ARQ', row: 1 },
        { id: 4, pos: 'DEF', label: 'LI', row: 2 },
        { id: 2, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 3, pos: 'DEF', label: 'DFC', row: 2 },
        { id: 1, pos: 'DEF', label: 'LD', row: 2 },
        { id: 5, pos: 'MED', label: 'MCD', row: 3 },
        { id: 6, pos: 'MED', label: 'MCD', row: 3 },
        { id: 9, pos: 'MED', label: 'MI', row: 3 },
        { id: 7, pos: 'MED', label: 'MCO', row: 3 },
        { id: 8, pos: 'MED', label: 'MD', row: 3 },
        { id: 10, pos: 'DEL', label: 'DC', row: 4 }
    ]
};

// Cambiar modo de juego (Normal / Solo Campeones)
function selectMode(mode) {
    selectedMode = mode;
    document.querySelectorAll('.mode-card[id^="mode-"]').forEach(el => el.classList.remove('active'));
    document.getElementById(`mode-${mode}`).classList.add('active');
}



// Elegir formación
function selectFormation(formation, btnEl) {
    selectedFormation = formation;
    document.querySelectorAll('.formation-btn').forEach(el => el.classList.remove('active'));
    btnEl.classList.add('active');
}

// Iniciar pantalla del Draft
function startDraft() {
    dreamTeam = Array(11).fill(null);
    draftProgress = 0;
    teamRating = 0.0;
    
    // Asignar re-sorteos
    resortCount = 2;
    
    // Inicializar pool de planteles de la ruleta
    const allPlanteles = window.plantelesData;
    const keys = Object.keys(allPlanteles);
    if (selectedMode === 'champions') {
        availablePlantelKeys = keys.filter(k => allPlanteles[k].is_champion === true);
    } else {
        availablePlantelKeys = keys;
    }
    
    selectedPlayerToPlace = null;
    isSpinning = false;
    currentSorteadoPlantel = null;
    
    // Switch de pantalla
    switchScreen('screen-draft');
    
    // Configurar labels del resort
    updateResortLabels();
    
    // Dibujar el campo y el box score
    renderFieldSlots();
    renderBoxScore();
    
    // Activar ruleta de inmediato
    document.getElementById('roulette-display').textContent = 'PRESIONA GIRAR';
    document.getElementById('btn-spin-roulette').disabled = false;
    document.getElementById('btn-resort-plantel').disabled = true;
    
    document.getElementById('draft-instructions').textContent = 'Gira la ruleta de planteles para iniciar la ronda 1';
    
    document.getElementById('draft-players-list').innerHTML = `
        <div style="text-align: center; color: var(--text-secondary); font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.75rem; padding: 2rem 0; text-transform: uppercase;">
            Gira la ruleta para revelar el primer plantel
        </div>
    `;
}

// Cambiar de pantalla del juego
function switchScreen(screenId) {
    document.querySelectorAll('.game-screen').forEach(el => el.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

// Actualizar textos de re-sorteo
function updateResortLabels() {
    const label = document.getElementById('resort-count-label');
    if (label) {
        label.textContent = `¿No te gustó? Re-sortea · ${resortCount} restantes`;
    }
}

// Renderizar grilla del campo tactico de circulos (con estado inactivo por defecto)
function renderFieldSlots() {
    const container = document.getElementById('field-rows-container');
    container.innerHTML = '';
    
    const slots = FORMACIONES[selectedFormation];
    
    for (let r = 4; r >= 1; r--) {
        const rowSlots = slots.filter(s => s.row === r);
        const rowDiv = document.createElement('div');
        rowDiv.className = 'field-row';
        
        rowSlots.forEach(slot => {
            const slotEl = document.createElement('div');
            slotEl.id = `circle-slot-${slot.id}`;
            slotEl.className = 'field-circle-slot';
            
            // Si tiene jugador asignado
            const player = dreamTeam[slot.id];
            if (player) {
                slotEl.className = 'field-circle-slot filled';
                slotEl.innerHTML = `
                    <span class="filled-rating">${player.rating}</span>
                    <span class="filled-name-badge">${player.name.split(' ').pop()}</span>
                `;
            } else {
                slotEl.innerHTML = `
                    <span class="circle-pos-label">${slot.label}</span>
                `;
            }
            
            rowDiv.appendChild(slotEl);
        });
        
        container.appendChild(rowDiv);
    }
}

// Renderizar Box Score lateral derecho
function renderBoxScore() {
    const slots = FORMACIONES[selectedFormation];
    const container = document.getElementById('box-score-positions-list');
    container.innerHTML = '';
    
    slots.forEach(slot => {
        const player = dreamTeam[slot.id];
        const row = document.createElement('div');
        row.className = 'box-score-row';
        
        row.innerHTML = `
            <span class="box-score-row-pos">${slot.label}</span>
            <span class="box-score-row-name">${player ? player.name : '————'}</span>
            <span class="box-score-row-rating">${player ? player.rating : '--'}</span>
        `;
        
        container.appendChild(row);
    });
    
    // Actualizar progreso
    document.getElementById('box-score-count').textContent = `${draftProgress} / 11`;
    
    // Actualizar rating enorme
    const ratingHuge = document.getElementById('box-score-rating');
    if (draftProgress === 0) {
        ratingHuge.textContent = '--';
    } else {
        ratingHuge.textContent = Math.round(teamRating);
    }
    
    // Actualizar barra de balance
    calculateTeamBalance();
}

// Calcular balance de Ataque vs Defensa
function calculateTeamBalance() {
    const filled = dreamTeam.filter(p => p !== null);
    const fillBar = document.getElementById('balance-bar-fill');
    const ratioText = document.getElementById('balance-ratio-text');
    
    if (filled.length === 0) {
        fillBar.style.width = '50%';
        ratioText.textContent = '50% / 50%';
        return;
    }
    
    let sumDef = 0;
    let countDef = 0;
    let sumAtk = 0;
    let countAtk = 0;
    
    filled.forEach(p => {
        if (p.pos === 'ARQ' || p.pos === 'DEF') {
            sumDef += p.rating;
            countDef++;
        } else {
            sumAtk += p.rating;
            countAtk++;
        }
    });
    
    const avgDef = countDef > 0 ? (sumDef / countDef) : 75.0;
    const avgAtk = countAtk > 0 ? (sumAtk / countAtk) : 75.0;
    
    const total = avgDef + avgAtk;
    const atkPct = Math.round((avgAtk / total) * 100);
    const defPct = 100 - atkPct;
    
    fillBar.style.width = `${atkPct}%`;
    ratioText.textContent = `${atkPct}% / ${defPct}%`;
}

// Iniciar animación de ruleta de planteles
function startRouletteSpin() {
    if (isSpinning || draftProgress >= 11) return;
    
    isSpinning = true;
    selectedPlayerToPlace = null;
    document.getElementById('btn-spin-roulette').disabled = true;
    document.getElementById('btn-resort-plantel').disabled = true;
    
    // Quitar cualquier destaque previo de la cancha
    renderFieldSlots();
    
    const display = document.getElementById('roulette-display');
    const allPlanteles = window.plantelesData;
    const keys = Object.keys(allPlanteles);
    
    // Filtrar planteles segun el modo y disponibilidad
    let eligibleKeys = [...availablePlantelKeys];
    if (eligibleKeys.length === 0) {
        eligibleKeys = keys;
    }
    
    // Seleccionar plantel al azar
    const randomKey = eligibleKeys[Math.floor(Math.random() * eligibleKeys.length)];
    const targetPlantel = allPlanteles[randomKey];
    
    // Animación de la ruleta (ciclado rápido desacelerando)
    let speed = 40; 
    let duration = 0;
    const maxDuration = 1800; // 1.8 segundos
    
    function spinCycle() {
        const tempKey = eligibleKeys[Math.floor(Math.random() * eligibleKeys.length)];
        display.textContent = allPlanteles[tempKey].name.replace(' (Campeón)', '').replace(' (Ballet Azul)', '').replace(' (Matador Salas)', '').replace(' (Racha Invicto)', '').replace(' (Vaccia)', '').replace(' (Apertura)', '').replace(' (Sampaoli)', '').replace(' (Triplete)', '').replace(' (Copa Chile)', '').replace(' (Soteldo)', '').replace(' (Transición)', '').replace(' (Larrivey)', '').replace(' (Osorio/Assadi)', '').replace(' (Pellegrino)', '').replace(' (Álvarez)', '').replace(' (Actual)', '').replace(' (Finalista)', '').replace(' (Semifinalista)', '').toUpperCase();
        
        duration += speed;
        
        if (duration < maxDuration) {
            if (duration > maxDuration * 0.7) {
                speed += 25;
            } else if (duration > maxDuration * 0.4) {
                speed += 12;
            }
            setTimeout(spinCycle, speed);
        } else {
            // Detener en el plantel real asignado
            display.textContent = targetPlantel.name.toUpperCase();
            currentSorteadoPlantel = targetPlantel;
            
            // Revelar la totalidad del plantel en el panel de la izquierda
            renderFullPlantelList(targetPlantel);
            
            isSpinning = false;
            document.getElementById('draft-instructions').textContent = 'Elige un jugador habilitado del plantel en la lista de la izquierda';
            
            // Habilitar re-sorteo si le quedan
            if (resortCount > 0) {
                document.getElementById('btn-resort-plantel').disabled = false;
            }
        }
    }
    
    spinCycle();
}

// Renderizar la totalidad del plantel en la lista de la izquierda
function renderFullPlantelList(plantel) {
    const container = document.getElementById('draft-players-list');
    container.innerHTML = '';
    
    const sortedPlayers = [...plantel.players].sort((a, b) => b.rating - a.rating);
    
    sortedPlayers.forEach((player, idx) => {
        const category = player.pos;
        
        // 1. Calcular si la posicion en el 11 ya esta completa
        const totalSlotsOfCategory = FORMACIONES[selectedFormation].filter(s => s.pos === category).length;
        const filledSlotsOfCategory = dreamTeam.filter((p, sIdx) => p !== null && FORMACIONES[selectedFormation][sIdx].pos === category).length;
        const slotsFree = totalSlotsOfCategory - filledSlotsOfCategory;
        const isFull = slotsFree <= 0;
        
        // 2. Comprobar si el jugador ya está seleccionado (para evitar duplicados obligatoriamente)
        const isAlreadyChosen = dreamTeam.some(p => p !== null && p.name.toLowerCase().trim() === player.name.toLowerCase().trim());
        
        const item = document.createElement('div');
        item.className = 'player-select-item';
        
        if (isAlreadyChosen) {
            item.style.opacity = '0.35';
            item.style.pointerEvents = 'none';
            item.innerHTML = `
                <div class="item-left">
                    <span class="item-number">#${idx + 1}</span>
                    <span class="item-name" style="text-decoration: line-through;">${player.name}</span>
                    <span class="item-pos">${player.pos}</span>
                </div>
                <span class="item-rating" style="font-size:0.65rem; font-family:'Montserrat',sans-serif; font-weight:800; color:var(--text-secondary);">ELEGIDO</span>
            `;
        } else if (isFull) {
            item.style.opacity = '0.35';
            item.style.pointerEvents = 'none';
            item.innerHTML = `
                <div class="item-left">
                    <span class="item-number">#${idx + 1}</span>
                    <span class="item-name" style="text-decoration: line-through;">${player.name}</span>
                    <span class="item-pos">${player.pos}</span>
                </div>
                <span class="item-rating" style="font-size:0.65rem; font-family:'Montserrat',sans-serif; font-weight:800; color:var(--accent-red);">LLENO</span>
            `;
        } else {
            item.onclick = () => selectPlayerForPlacement(player, item);
            item.innerHTML = `
                <div class="item-left">
                    <span class="item-number">#${idx + 1}</span>
                    <span class="item-name">${player.name}</span>
                    <span class="item-pos">${player.pos}</span>
                </div>
                <span class="item-rating">${player.rating}</span>
            `;
        }
        
        container.appendChild(item);
    });
}

// Re-sortear plantel
function resortPlantel() {
    if (resortCount <= 0 || isSpinning) return;
    resortCount--;
    updateResortLabels();
    startRouletteSpin();
}

// Al seleccionar un jugador de la lista
function selectPlayerForPlacement(player, itemEl) {
    if (isSpinning) return;
    
    document.querySelectorAll('.player-select-item').forEach(el => el.classList.remove('selected'));
    itemEl.classList.add('selected');
    selectedPlayerToPlace = player;
    
    renderFieldSlots();
    
    const category = player.pos;
    const slots = FORMACIONES[selectedFormation];
    
    slots.forEach(slot => {
        if (slot.pos === category && dreamTeam[slot.id] === null) {
            const circle = document.getElementById(`circle-slot-${slot.id}`);
            if (circle) {
                circle.classList.add('highlight-slot');
                circle.onclick = () => placePlayerInSlot(slot.id);
            }
        }
    });
    
    document.getElementById('draft-instructions').textContent = `Toca un círculo parpadeante en la cancha para posicionar a ${player.name} (${player.pos})`;
}

// Ubicar jugador en el slot elegido
function placePlayerInSlot(slotId) {
    if (!selectedPlayerToPlace) return;
    
    // Si estamos en modo Solo Campeones, removemos el plantel del pool disponible para no repetirlo
    if (selectedMode === 'champions' && currentSorteadoPlantel) {
        const allPlanteles = window.plantelesData;
        const keyToRemove = Object.keys(allPlanteles).find(k => allPlanteles[k].name === currentSorteadoPlantel.name);
        if (keyToRemove) {
            availablePlantelKeys = availablePlantelKeys.filter(k => k !== keyToRemove);
        }
    }
    
    dreamTeam[slotId] = {
        name: selectedPlayerToPlace.name,
        pos: selectedPlayerToPlace.pos,
        rating: selectedPlayerToPlace.rating,
        year: currentSorteadoPlantel.year
    };
    
    draftProgress++;
    selectedPlayerToPlace = null;
    
    recalculateTeamRating();
    renderFieldSlots();
    renderBoxScore();
    
    document.getElementById('roulette-display').textContent = 'PRESIONA GIRAR';
    document.getElementById('btn-spin-roulette').disabled = false;
    document.getElementById('btn-resort-plantel').disabled = true;
    
    document.getElementById('draft-players-list').innerHTML = `
        <div style="text-align: center; color: var(--text-secondary); font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.75rem; padding: 2rem 0; text-transform: uppercase;">
            Gira la ruleta para la siguiente ronda (${draftProgress + 1}/11)
        </div>
    `;
    
    document.getElementById('draft-instructions').textContent = 'Gira la ruleta de planteles para la siguiente ronda';
    
    if (draftProgress === 11) {
        document.getElementById('btn-advance-tournament').style.display = 'block';
        document.getElementById('btn-spin-roulette').disabled = true;
        document.getElementById('roulette-display').textContent = '¡COMPLETO!';
        document.getElementById('draft-instructions').textContent = '¡11 completado con éxito! Presiona el botón de abajo para avanzar al torneo.';
    }
}

// Recalcular rating general
function recalculateTeamRating() {
    const filled = dreamTeam.filter(p => p !== null);
    if (filled.length === 0) {
        teamRating = 0.0;
    } else {
        const sum = filled.reduce((acc, p) => acc + p.rating, 0);
        teamRating = sum / filled.length;
    }
}

// Setup del torneo
function goToTournamentSetup() {
    document.getElementById('summary-formation').textContent = selectedFormation;
    document.getElementById('summary-rating').textContent = teamRating.toFixed(1);
    switchScreen('screen-tournament-setup');
}

// Generar oponentes y fixture del torneo
function generateTournament() {
    teamName = document.getElementById('input-team-name').value.trim() || "U. DE CHILE HISTÓRICA";
    teamName = teamName.toUpperCase();
    
    const userTeam = {
        id: 0,
        name: teamName,
        rating: teamRating,
        is_user: true,
        players: dreamTeam,
        pts: 0, pj: 0, gf: 0, gc: 0
    };
    
    tournamentTeams = []; // Bolsa de rivales posibles
    
    const allPlanteles = window.plantelesData;
    const keys = Object.keys(allPlanteles);
    
    // Obtenemos solo los campeones reales para los rivales
    const championKeys = keys.filter(k => allPlanteles[k].is_champion === true);
    
    championKeys.forEach((key) => {
        const p = allPlanteles[key];
        const sum = p.players.reduce((acc, pl) => acc + pl.rating, 0);
        let avg = sum / p.players.length;
        
        tournamentTeams.push({
            id: tournamentTeams.length,
            name: p.name.toUpperCase(),
            rating: avg,
            is_user: false,
            players: p.players,
            pts: 0, pj: 0, gf: 0, gc: 0
        });
    });
    
    // Barajamos todos los rivales posibles de forma aleatoria
    const shuffledRivals = tournamentTeams.sort(() => 0.5 - Math.random());
    
    // Guardamos la lista barajada para ir tomando los rivales de forma única y consecutiva
    tournamentTeams = shuffledRivals;
    
    groupStandings = [userTeam, shuffledRivals[0], shuffledRivals[1], shuffledRivals[2]];
    
    groupStandings.forEach(t => {
        t.pts = 0; t.pj = 0; t.gf = 0; t.gc = 0;
    });
    
    currentMatchIndex = 0;
    tournamentStage = "groups";
    
    switchScreen('screen-tournament');
    document.getElementById('tournament-team-title').textContent = `MUNDIAL DE LEYENDAS · ${teamName}`;
    
    updateGroupTable();
    updateFixtureView();
    setupNextMatchSimulation();
}

// Actualizar tabla del grupo
function updateGroupTable() {
    const sorted = [...groupStandings].sort((a, b) => {
        if (b.pts !== a.pts) return b.pts - a.pts;
        const diffA = a.gf - a.gc;
        const diffB = b.gf - b.gc;
        if (diffB !== diffA) return diffB - diffA;
        return b.gf - a.gf;
    });
    
    const tbody = document.getElementById('group-table-body');
    tbody.innerHTML = '';
    
    sorted.forEach((team, idx) => {
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid rgba(0,0,0,0.1)';
        if (team.is_user) {
            row.style.background = 'rgba(37,99,235,0.08)';
            row.style.fontWeight = '800';
        }
        
        let cleanName = team.name.replace(' (CAMPEÓN)', '').replace(' (BALLET AZUL)', '').replace(' (MATADOR SALAS)', '').replace(' (RACHA INVICTO)', '');
        row.innerHTML = `
            <td style="padding: 0.6rem 0; font-family: 'Montserrat', sans-serif; font-weight: 800; color: var(--text-primary);">
                ${idx + 1}. ${cleanName} <span style="font-size:0.7rem; color:var(--text-secondary);">(${team.rating.toFixed(1)})</span>
            </td>
            <td style="text-align: center; font-weight: 800; color: var(--text-primary);">${team.pts}</td>
            <td style="text-align: center; color: var(--text-secondary);">${team.pj}</td>
            <td style="text-align: center; color: var(--text-secondary);">${team.gf}</td>
            <td style="text-align: center; color: var(--text-secondary);">${team.gc}</td>
        `;
        tbody.appendChild(row);
    });
}

// Actualizar fixture
function updateFixtureView() {
    const container = document.getElementById('fixture-matches-container');
    container.innerHTML = '';
    
    if (tournamentStage === "groups") {
        document.getElementById('fixture-stage-title').textContent = 'Fase de Grupos (Clasifican 2)';
        
        const matches = [
            { stage: "Fecha 1", home: groupStandings[0], away: groupStandings[1], played: currentMatchIndex > 0 },
            { stage: "Fecha 2", home: groupStandings[0], away: groupStandings[2], played: currentMatchIndex > 1 },
            { stage: "Fecha 3", home: groupStandings[0], away: groupStandings[3], played: currentMatchIndex > 2 }
        ];
        
        matches.forEach((m, idx) => {
            const row = document.createElement('div');
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.style.alignItems = 'center';
            row.style.padding = '0.6rem';
            row.style.border = '2px solid var(--text-primary)';
            if (idx === currentMatchIndex) {
                row.style.background = 'rgba(37,99,235,0.04)';
                row.style.borderColor = 'var(--accent-red)';
            }
            
            let cleanHomeName = m.home.name.replace(' (CAMPEÓN)', '').replace(' (BALLET AZUL)', '').replace(' (MATADOR SALAS)', '').replace(' (RACHA INVICTO)', '');
            let cleanAwayName = m.away.name.replace(' (CAMPEÓN)', '').replace(' (BALLET AZUL)', '').replace(' (MATADOR SALAS)', '').replace(' (RACHA INVICTO)', '');

            row.innerHTML = `
                <span style="font-weight: 800; font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">${m.stage}</span>
                <span style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.8rem; text-transform: uppercase; color: var(--text-primary);">
                    ${cleanHomeName.substring(0, 14)} vs ${cleanAwayName.substring(0, 14)}
                </span>
                <span style="font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem; color: var(--text-primary);">
                    ${m.played ? "JUGADO" : (idx === currentMatchIndex ? "POR JUGAR" : "PENDIENTE")}
                </span>
            `;
            container.appendChild(row);
        });
    } else {
        document.getElementById('fixture-stage-title').textContent = playoffStageNames[playoffStageIndex];
        
        const row = document.createElement('div');
        row.style.display = 'flex';
        row.style.justifyContent = 'space-between';
        row.style.alignItems = 'center';
        row.style.padding = '0.8rem';
        row.style.border = '3px solid var(--text-primary)';
        row.style.background = 'rgba(37,99,235,0.05)';
        
        let cleanHomeName = groupStandings[0].name.replace(' (CAMPEÓN)', '').replace(' (BALLET AZUL)', '').replace(' (MATADOR SALAS)', '').replace(' (RACHA INVICTO)', '');
        let cleanAwayName = playoffOpponent.name.replace(' (CAMPEÓN)', '').replace(' (BALLET AZUL)', '').replace(' (MATADOR SALAS)', '').replace(' (RACHA INVICTO)', '');

        row.innerHTML = `
            <span style="font-weight: 800; font-size: 0.8rem; color: var(--accent-red); text-transform: uppercase;">MANDATORIO</span>
            <span style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.9rem; text-transform: uppercase; color: var(--text-primary);">
                ${cleanHomeName.substring(0, 14)} vs ${cleanAwayName.substring(0, 14)}
            </span>
            <span style="font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem; color: var(--text-primary);">
                PLAYOFFS
            </span>
        `;
        container.appendChild(row);
    }
}

// Click del botón central de simulación (Controlador Central)
function handleStartSimClick() {
    const btn = document.getElementById('btn-start-sim');
    const action = btn.getAttribute('data-action');
    
    if (action === 'simulate') {
        simulateActiveMatch();
    } else if (action === 'setup') {
        setupNextMatchSimulation();
    } else if (action === 'gameover') {
        const isWinner = sessionStorage.getItem('gameover_winner') === 'true';
        const msg = sessionStorage.getItem('gameover_msg') || "Fin del juego.";
        endGame(isWinner, msg);
    }
}

// Configurar proximo partido
function setupNextMatchSimulation() {
    let home, away;
    
    if (tournamentStage === "groups") {
        document.getElementById('match-sim-phase').textContent = `FECHA ${currentMatchIndex + 1}`;
        home = groupStandings[0];
        if (currentMatchIndex === 0) away = groupStandings[1];
        else if (currentMatchIndex === 1) away = groupStandings[2];
        else away = groupStandings[3];
    } else {
        document.getElementById('match-sim-phase').textContent = playoffStageNames[playoffStageIndex].toUpperCase();
        home = groupStandings[0];
        away = playoffOpponent;
    }
    
    // Limpiar nombre del rival
    let cleanAwayName = away.name.replace(' (CAMPEÓN)', '').replace(' (BALLET AZUL)', '').replace(' (MATADOR SALAS)', '').replace(' (RACHA INVICTO)', '');
    document.getElementById('sim-away-name').textContent = cleanAwayName;
    document.getElementById('sim-scoreboard').textContent = "0 - 0";
    
    // Ocultar bitácora, temporizador y caja de penales
    document.getElementById('sim-timer').style.display = 'none';
    document.getElementById('sim-events-log').style.display = 'none';
    document.getElementById('sim-events-log').innerHTML = '';
    
    document.getElementById('sim-penalties-card').style.display = 'none';
    document.getElementById('pen-current-kicker-banner').style.display = 'block';
    
    const btn = document.getElementById('btn-start-sim');
    btn.disabled = false;
    btn.textContent = "JUGAR PARTIDO";
    btn.setAttribute('data-action', 'simulate');
}

// Simular partido
function simulateActiveMatch() {
    const btn = document.getElementById('btn-start-sim');
    btn.disabled = true;
    
    const logEl = document.getElementById('sim-events-log');
    const timerEl = document.getElementById('sim-timer');
    
    logEl.style.display = 'flex';
    timerEl.style.display = 'inline-block';
    logEl.innerHTML = '';
    
    let home, away;
    if (tournamentStage === "groups") {
        home = groupStandings[0];
        if (currentMatchIndex === 0) away = groupStandings[1];
        else if (currentMatchIndex === 1) away = groupStandings[2];
        else away = groupStandings[3];
    } else {
        home = groupStandings[0];
        away = playoffOpponent;
    }
    
    let scoreHome = 0;
    let scoreAway = 0;
    let minute = 0;
    
    const interval = setInterval(() => {
        minute += 3;
        if (minute > 90) minute = 90;
        timerEl.textContent = `${minute}'`;
        
        const diff = home.rating - away.rating;
        const probHome = Math.max(0.01, Math.min(0.25, 0.075 + (diff * 0.01)));
        const probAway = Math.max(0.01, Math.min(0.25, 0.075 - (diff * 0.01)));
        
        if (Math.random() < probHome) {
            scoreHome++;
            const scorer = chooseScorer(home);
            const lastName = scorer.split(' ').pop().toUpperCase();
            
            logEl.innerHTML += `
                <div class="event-row" style="animation: fadeInUp 0.3s ease;">
                    <span class="event-minute">${minute}'</span>
                    <span class="event-icon">⚽</span>
                    <span class="event-text" style="color: #15803d;">${lastName}</span>
                </div>
            `;
            document.getElementById('sim-scoreboard').textContent = `${scoreHome} - ${scoreAway}`;
            logEl.scrollTop = logEl.scrollHeight;
        }
        
        if (Math.random() < probAway) {
            scoreAway++;
            const scorer = chooseScorer(away);
            const lastName = scorer.split(' ').pop().toUpperCase();
            
            logEl.innerHTML += `
                <div class="event-row" style="animation: fadeInUp 0.3s ease;">
                    <span class="event-minute">${minute}'</span>
                    <span class="event-icon">⚽</span>
                    <span class="event-text" style="color: #ef4444;">${lastName}</span>
                </div>
            `;
            document.getElementById('sim-scoreboard').textContent = `${scoreHome} - ${scoreAway}`;
            logEl.scrollTop = logEl.scrollHeight;
        }
        
        if (minute >= 90) {
            clearInterval(interval);
            processMatchResult(scoreHome, scoreAway, home, away);
        }
    }, 150);
}

// Goleador al azar
function chooseScorer(team) {
    if (!team.players || team.players.length === 0) {
        return "Leyenda Azul";
    }
    const weighted = [];
    team.players.forEach(p => {
        let weight = 1;
        if (p.pos === 'DEL') weight = 6;
        else if (p.pos === 'MED') weight = 3;
        else if (p.pos === 'DEF') weight = 1;
        else weight = 0.01;
        
        for (let i = 0; i < weight * 10; i++) {
            weighted.push(p.name);
        }
    });
    return weighted[Math.floor(Math.random() * weighted.length)];
}

// Procesar resultado
function processMatchResult(scoreHome, scoreAway, home, away) {
    const btn = document.getElementById('btn-start-sim');
    btn.disabled = false;
    
    if (tournamentStage === "groups") {
        home.pj++;
        away.pj++;
        home.gf += scoreHome;
        home.gc += scoreAway;
        away.gf += scoreAway;
        away.gc += scoreHome;
        
        if (scoreHome > scoreAway) {
            home.pts += 3;
        } else if (scoreHome < scoreAway) {
            away.pts += 3;
        } else {
            home.pts += 1;
            away.pts += 1;
        }
        
        simulateOtherGroupMatches();
        currentMatchIndex++;
        
        updateGroupTable();
        updateFixtureView();
        
        if (currentMatchIndex < 3) {
            btn.textContent = "SIGUIENTE FECHA";
            btn.setAttribute('data-action', 'setup');
        } else {
            const sorted = [...groupStandings].sort((a, b) => {
                if (b.pts !== a.pts) return b.pts - a.pts;
                const diffA = a.gf - a.gc;
                const diffB = b.gf - b.gc;
                if (diffB !== diffA) return diffB - diffA;
                return b.gf - a.gf;
            });
            
            const userRank = sorted.findIndex(t => t.is_user) + 1;
            
            if (userRank <= 2) {
                tournamentStage = "playoffs";
                playoffStageIndex = 0;
                playoffOpponent = selectPlayoffOpponent();
                
                btn.textContent = "AVANZAR A OCTAVOS DE FINAL";
                btn.setAttribute('data-action', 'setup');
            } else {
                btn.textContent = "VER RESULTADOS";
                btn.setAttribute('data-action', 'gameover');
                
                // Guardar mensaje en sessionStorage para mostrarlo al hacer click
                sessionStorage.setItem('gameover_msg', `Quedaste en el puesto #${userRank} del grupo. ¡Casi clasificas!`);
                sessionStorage.setItem('gameover_winner', 'false');
            }
        }
    } else {
        if (scoreHome > scoreAway) {
            advancePlayoffs();
        } else if (scoreHome < scoreAway) {
            btn.textContent = "VER RESULTADOS";
            btn.setAttribute('data-action', 'gameover');
            sessionStorage.setItem('gameover_msg', `Derrotado en ${playoffStageNames[playoffStageIndex]} frente a ${away.name.replace(' (CAMPEÓN)', '')}.`);
            sessionStorage.setItem('gameover_winner', 'false');
        } else {
            simulatePenalties(home, away);
        }
    }
}

// Simular penales en Playoffs
function simulatePenalties(home, away) {
    const btn = document.getElementById('btn-start-sim');
    btn.disabled = true;
    
    const penaltiesCard = document.getElementById('sim-penalties-card');
    penaltiesCard.style.display = 'flex';
    
    const localList = document.getElementById('pen-local-list');
    const awayList = document.getElementById('pen-away-list');
    const vsList = document.getElementById('pen-vs-separator');
    const kickerNameSpan = document.getElementById('pen-kicker-name');
    
    localList.innerHTML = '';
    awayList.innerHTML = '';
    vsList.innerHTML = '';
    
    let pensHome = 0;
    let pensAway = 0;
    
    // Extraer jugadores reales de los planteles para patear
    const localKickers = [...home.players].filter(p => p !== null).sort(() => 0.5 - Math.random());
    const awayKickers = [...away.players].filter(p => p !== null).sort(() => 0.5 - Math.random());
    
    let isLocalTurn = true;
    let shotIndex = 0;
    
    const interval = setInterval(() => {
        const localShots = Math.floor(shotIndex / 2) + (shotIndex % 2);
        const awayShots = Math.floor(shotIndex / 2);
        
        // Verificar si la tanda ya está decidida matemáticamente
        if (shotIndex >= 10) {
            // Muerte súbita: termina si después de un par completo de tiros hay diferencia
            if (localShots === awayShots && pensHome !== pensAway) {
                finalizeShootout();
                return;
            }
        } else {
            // Tanda regular de 5 disparos por lado
            const localRemaining = 5 - localShots;
            const awayRemaining = 5 - awayShots;
            
            if (pensHome > pensAway + awayRemaining || pensAway > pensHome + localRemaining) {
                finalizeShootout();
                return;
            }
        }
        
        if (isLocalTurn) {
            const kicker = localKickers[localShots % localKickers.length] || { name: "Leyenda Azul" };
            const lastName = kicker.name.split(' ').pop().toUpperCase();
            kickerNameSpan.textContent = `${home.name.replace(' (CAMPEÓN)', '').replace(' (BALLET AZUL)', '').replace(' (MATADOR SALAS)', '').replace(' (RACHA INVICTO)', '').substring(0, 10)}: ${lastName}`;
            
            const isGoal = Math.random() < 0.75;
            if (isGoal) pensHome++;
            
            const badge = isGoal 
                ? `<span style="background: #dcfce7; color: #15803d; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.75rem; margin-right: 0.5rem; border: 1.5px solid #16a34a;">⚽</span>` 
                : `<span style="background: #fee2e2; color: #ef4444; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.75rem; margin-right: 0.5rem; border: 1.5px solid #dc2626;">❌</span>`;
            
            localList.innerHTML += `
                <div style="display: flex; align-items: center; font-family: 'Montserrat', sans-serif; font-size: 0.85rem; font-weight: 800; animation: fadeInUp 0.3s ease;">
                    ${badge}
                    <span>${lastName}</span>
                </div>
            `;
            
            vsList.innerHTML += `<div style="height: 22px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: var(--text-secondary); opacity: 0.5;">vs</div>`;
            
            document.getElementById('sim-scoreboard').textContent = `${pensHome} - ${pensAway}`;
            isLocalTurn = false;
        } else {
            const kicker = awayKickers[awayShots % awayKickers.length] || { name: "Rival" };
            const lastName = kicker.name.split(' ').pop().toUpperCase();
            kickerNameSpan.textContent = `${away.name.replace(' (CAMPEÓN)', '').replace(' (BALLET AZUL)', '').replace(' (MATADOR SALAS)', '').replace(' (RACHA INVICTO)', '').substring(0, 10)}: ${lastName}`;
            
            const isGoal = Math.random() < 0.75;
            if (isGoal) pensAway++;
            
            const badge = isGoal 
                ? `<span style="background: #dcfce7; color: #15803d; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.75rem; margin-left: 0.5rem; border: 1.5px solid #16a34a;">⚽</span>` 
                : `<span style="background: #fee2e2; color: #ef4444; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.75rem; margin-left: 0.5rem; border: 1.5px solid #dc2626;">❌</span>`;
            
            awayList.innerHTML += `
                <div style="display: flex; align-items: center; font-family: 'Montserrat', sans-serif; font-size: 0.85rem; font-weight: 800; animation: fadeInUp 0.3s ease;">
                    <span>${lastName}</span>
                    ${badge}
                </div>
            `;
            
            document.getElementById('sim-scoreboard').textContent = `${pensHome} - ${pensAway}`;
            isLocalTurn = true;
        }
        
        shotIndex++;
    }, 1200);
    
    function finalizeShootout() {
        clearInterval(interval);
        
        document.getElementById('pen-current-kicker-banner').style.display = 'none';
        
        btn.disabled = false;
        if (pensHome > pensAway) {
            advancePlayoffs();
        } else {
            btn.textContent = "VER RESULTADOS";
            btn.setAttribute('data-action', 'gameover');
            sessionStorage.setItem('gameover_msg', `Fuiste eliminado en penales (${pensHome}-${pensAway}) en ${playoffStageNames[playoffStageIndex]} frente a ${away.name.replace(' (CAMPEÓN)', '')}.`);
            sessionStorage.setItem('gameover_winner', 'false');
        }
    }
}

// Avanzar playoffs
function advancePlayoffs() {
    playoffStageIndex++;
    if (playoffStageIndex < 4) {
        playoffOpponent = selectPlayoffOpponent();
        const btn = document.getElementById('btn-start-sim');
        btn.textContent = "SIGUIENTE RONDA";
        btn.setAttribute('data-action', 'setup');
    } else {
        const btn = document.getElementById('btn-start-sim');
        btn.textContent = "VER RESULTADOS";
        btn.setAttribute('data-action', 'gameover');
        sessionStorage.setItem('gameover_msg', `¡Increíble hazaña! Tu Dream Team se coronó Campeón del Torneo Mundial de Leyendas.`);
        sessionStorage.setItem('gameover_winner', 'true');
    }
}

// Oponente de playoffs
function selectPlayoffOpponent() {
    // Los rivales de grupo son los índices 0, 1 y 2 de la lista barajada.
    // Los rivales de playoffs (Octavos, Cuartos, Semis, Final) serán los índices 3, 4, 5 y 6.
    return tournamentTeams[3 + playoffStageIndex];
}

// Simular resto del grupo
function simulateOtherGroupMatches() {
    let home, away;
    if (currentMatchIndex === 0) {
        home = groupStandings[2];
        away = groupStandings[3];
    } else if (currentMatchIndex === 1) {
        home = groupStandings[1];
        away = groupStandings[3];
    } else {
        home = groupStandings[1];
        away = groupStandings[2];
    }
    
    const diff = home.rating - away.rating;
    const probHome = 0.35 + (diff * 0.02);
    const probDraw = 0.30;
    
    const roll = Math.random();
    let gfHome = 0;
    let gfAway = 0;
    
    if (roll < probHome) {
        gfHome = Math.floor(Math.random() * 3) + 1;
        gfAway = Math.floor(Math.random() * gfHome);
    } else if (roll < probHome + probDraw) {
        gfHome = Math.floor(Math.random() * 2);
        gfAway = gfHome;
    } else {
        gfAway = Math.floor(Math.random() * 3) + 1;
        gfHome = Math.floor(Math.random() * gfAway);
    }
    
    home.pj++;
    away.pj++;
    home.gf += gfHome;
    home.gc += gfAway;
    away.gf += gfAway;
    away.gc += gfHome;
    
    if (gfHome > gfAway) {
        home.pts += 3;
    } else if (gfHome < gfAway) {
        away.pts += 3;
    } else {
        home.pts += 1;
        away.pts += 1;
    }
}

// Fin del juego
function endGame(isWinner, message) {
    switchScreen('screen-gameover');
    
    const icon = document.getElementById('gameover-status-icon');
    const title = document.getElementById('gameover-title');
    const msg = document.getElementById('gameover-msg');
    const btnSave = document.getElementById('btn-save-muro');
    
    if (isWinner) {
        icon.textContent = "🏆";
        title.textContent = "¡CAMPEÓN DEL MUNDO!";
        title.style.color = "var(--text-primary)";
        msg.textContent = message;
        if (btnSave) btnSave.style.display = 'block';
    } else {
        icon.textContent = "❌";
        title.textContent = "ELIMINADO";
        title.style.color = "var(--accent-red)";
        msg.textContent = message;
        if (btnSave) btnSave.style.display = 'none';
    }
}

// Reiniciar juego
function restartGame() {
    sessionStorage.removeItem('gameover_winner');
    sessionStorage.removeItem('gameover_msg');
    window.location.reload();
}

// Guardar
function saveToHallOfFame() {
    const btn = document.getElementById('btn-save-muro');
    if (!btn) return;
    
    btn.disabled = true;
    btn.textContent = "GUARDANDO...";
    
    const payload = {
        team_name: teamName,
        formation: selectedFormation,
        rating: teamRating,
        players: dreamTeam
    };
    
    fetch('/api/juego/guardar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.status === 401) {
            alert("Debes iniciar sesión para registrar tu Dream Team en el Muro de Honor.");
            throw new Error("No autenticado");
        }
        return res.json();
    })
    .then(data => {
        alert(data.message || "¡Tu equipo ha sido inmortalizado!");
        window.location.href = "/juego";
    })
    .catch(err => {
        console.error(err);
        btn.disabled = false;
        btn.textContent = "INMORTALIZAR EN MURO DE HONOR";
    });
}

// Auto-completar Dream Team con jugadores estrella de forma automática (para pruebas)
function autoDraftCheat() {
    const allPlanteles = window.plantelesData;
    const slots = FORMACIONES[selectedFormation];
    
    // Reunimos a todos los jugadores disponibles en una sola lista plana
    let allPlayers = [];
    Object.keys(allPlanteles).forEach(key => {
        const p = allPlanteles[key];
        p.players.forEach(pl => {
            allPlayers.push({
                name: pl.name,
                pos: pl.pos,
                rating: pl.rating,
                year: p.year
            });
        });
    });
    
    // Los ordenamos por rating descendente para priorizar a las leyendas
    allPlayers.sort((a, b) => b.rating - a.rating);
    
    // Llenamos cada slot buscando al mejor jugador disponible para esa categoría
    const selectedNames = new Set();
    dreamTeam = Array(11).fill(null);
    
    slots.forEach(slot => {
        const found = allPlayers.find(pl => 
            pl.pos === slot.pos && !selectedNames.has(pl.name.toLowerCase())
        );
        if (found) {
            dreamTeam[slot.id] = {
                name: found.name,
                pos: found.pos,
                rating: found.rating,
                year: found.year
            };
            selectedNames.add(found.name.toLowerCase());
        }
    });
    
    draftProgress = 11;
    recalculateTeamRating();
    renderFieldSlots();
    renderBoxScore();
    
    // Activar avances
    document.getElementById('btn-advance-tournament').style.display = 'block';
    document.getElementById('btn-spin-roulette').disabled = true;
    document.getElementById('roulette-display').textContent = '¡COMPLETO!';
    document.getElementById('draft-instructions').textContent = '¡Equipo autocompletado con las mejores leyendas! Presiona el botón de abajo para avanzar.';
}
