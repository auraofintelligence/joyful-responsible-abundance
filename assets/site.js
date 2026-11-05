/* Small, local enhancements. Reading and navigation do not depend on this file. */
(() => {
  'use strict';

  const backTop = document.querySelector('.back-top');
  if (backTop) {
    const showReturnLink = () => {
      backTop.classList.toggle('is-floating', window.scrollY > window.innerHeight);
    };
    window.addEventListener('scroll', showReturnLink, { passive: true });
    showReturnLink();
  }

  const normalise = (value) => String(value || '')
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase('en-AU')
    .trim();

  const searchInput = document.getElementById('library-search');
  const categorySelect = document.getElementById('category-filter');
  const countOutput = document.getElementById('result-count');
  const searchableItems = Array.from(document.querySelectorAll('[data-search]'));

  if (searchableItems.length && (searchInput || categorySelect)) {
    const applyFilter = () => {
      const terms = normalise(searchInput ? searchInput.value : '').split(/\s+/).filter(Boolean);
      const selectedCategory = normalise(categorySelect ? categorySelect.value : '');
      const allCategories = !selectedCategory || selectedCategory === 'all' || selectedCategory === '*';
      let visibleCount = 0;

      searchableItems.forEach((item) => {
        const searchText = normalise(item.dataset.search || item.textContent);
        const category = normalise(item.dataset.category);
        const matchesText = terms.every((term) => searchText.includes(term));
        const matchesCategory = allCategories || category === selectedCategory;
        const visible = matchesText && matchesCategory;
        item.hidden = !visible;
        if (visible) visibleCount += 1;
      });

      if (countOutput) {
        const noun = countOutput.dataset.noun || 'item';
        const plural = countOutput.dataset.plural || `${noun}s`;
        countOutput.textContent = `${visibleCount.toLocaleString('en-AU')} ${visibleCount === 1 ? noun : plural} shown`;
        countOutput.setAttribute('aria-live', 'polite');
        countOutput.setAttribute('role', 'status');
      }
    };

    if (searchInput) searchInput.addEventListener('input', applyFilter);
    if (categorySelect) categorySelect.addEventListener('change', applyFilter);
    applyFilter();
  }

  const calculator = document.getElementById('compute-calculator');
  const siteCount = document.getElementById('site-count');
  const siteCost = document.getElementById('site-cost');
  const totalOutput = document.getElementById('compute-total');
  const detailOutput = document.getElementById('compute-detail');
  const errorOutput = document.getElementById('compute-error');

  if (calculator && siteCount && siteCost && totalOutput) {
    const numberFormat = new Intl.NumberFormat('en-AU', { maximumFractionDigits: 2 });
    const detailFormat = new Intl.NumberFormat('en-AU', { maximumFractionDigits: 6 });
    const presets = Array.from(calculator.querySelectorAll('[data-sites][data-cost]'));

    const describeMillions = (millions, precise = false) => {
      const format = precise ? detailFormat : numberFormat;
      if (millions >= 1000000) return `A$${format.format(millions / 1000000)} trillion`;
      if (millions >= 1000) return `A$${format.format(millions / 1000)} billion`;
      return `A$${format.format(millions)} million`;
    };

    const updateCalculator = () => {
      const sites = Number(siteCount.value);
      const cost = Number(siteCost.value);
      const validSites = siteCount.value.trim() !== '' && Number.isFinite(sites)
        && Number.isInteger(sites) && sites >= 1 && sites <= 1000000;
      const validCost = siteCost.value.trim() !== '' && Number.isFinite(cost)
        && cost >= 0.01 && cost <= 1000;

      siteCount.setAttribute('aria-invalid', String(!validSites));
      siteCost.setAttribute('aria-invalid', String(!validCost));

      if (!validSites || !validCost) {
        totalOutput.textContent = 'Check the figures';
        if (detailOutput) detailOutput.textContent = 'Enter valid figures to calculate an indicative total.';
        if (errorOutput) {
          errorOutput.textContent = !validSites
            ? 'Enter a whole number of sites from 1 to 1,000,000.'
            : 'Enter a cost per site from A$0.01 million to A$1,000 million.';
          errorOutput.hidden = false;
        }
        presets.forEach((button) => button.setAttribute('aria-pressed', 'false'));
        return;
      }

      if (errorOutput) {
        errorOutput.textContent = '';
        errorOutput.hidden = true;
      }

      const totalMillions = sites * cost;
      totalOutput.textContent = describeMillions(totalMillions);
      if (detailOutput) {
        detailOutput.textContent = `${sites.toLocaleString('en-AU')} ${sites === 1 ? 'site' : 'sites'} × A$${detailFormat.format(cost)} million per site = ${describeMillions(totalMillions, true)} in initial capital.`;
      }
      presets.forEach((button) => {
        const selected = Number(button.dataset.sites) === sites && Number(button.dataset.cost) === cost;
        button.setAttribute('aria-pressed', String(selected));
      });
    };

    calculator.addEventListener('submit', (event) => {
      event.preventDefault();
      updateCalculator();
    });
    siteCount.addEventListener('input', updateCalculator);
    siteCost.addEventListener('input', updateCalculator);
    presets.forEach((button) => {
      button.type = 'button';
      button.addEventListener('click', () => {
        siteCount.value = button.dataset.sites;
        siteCost.value = button.dataset.cost;
        updateCalculator();
      });
    });
    if (!siteCount.value) siteCount.value = '3000';
    if (!siteCost.value) siteCost.value = '6';
    updateCalculator();
  }

  const energyCalculator = document.getElementById('energy-calculator');
  const powerInput = document.getElementById('power-gw');
  const utilisationInput = document.getElementById('utilisation');
  const energyTotal = document.getElementById('energy-total');
  const energyComparison = document.getElementById('energy-comparison');
  const energyError = document.getElementById('energy-error');

  if (energyCalculator && powerInput && utilisationInput && energyTotal && energyComparison) {
    const annualBaseline = 286.8;
    const energyFormat = new Intl.NumberFormat('en-AU', { maximumFractionDigits: 6 });
    const percentFormat = new Intl.NumberFormat('en-AU', { maximumFractionDigits: 1 });
    const smallPercentFormat = new Intl.NumberFormat('en-AU', { maximumFractionDigits: 4 });
    const energyPresets = Array.from(energyCalculator.querySelectorAll('[data-gw]'));

    const updateEnergy = () => {
      const power = Number(powerInput.value);
      const utilisation = Number(utilisationInput.value);
      const validPower = powerInput.value.trim() !== '' && Number.isFinite(power)
        && power >= 0.01 && power <= 10000;
      const validUtilisation = utilisationInput.value.trim() !== '' && Number.isFinite(utilisation)
        && Number.isInteger(utilisation) && utilisation >= 1 && utilisation <= 100;

      powerInput.setAttribute('aria-invalid', String(!validPower));
      utilisationInput.setAttribute('aria-invalid', String(!validUtilisation));
      if (!validPower || !validUtilisation) {
        energyTotal.textContent = 'Check the figures';
        energyComparison.textContent = 'Enter valid figures to calculate annual energy use.';
        if (energyError) {
          energyError.textContent = !validPower
            ? 'Enter a power level from 0.01 to 10,000 gigawatts.'
            : 'Enter a whole-number utilisation percentage from 1 to 100.';
          energyError.hidden = false;
        }
        energyPresets.forEach((button) => button.setAttribute('aria-pressed', 'false'));
        return;
      }

      if (energyError) {
        energyError.textContent = '';
        energyError.hidden = true;
      }
      const annualEnergy = power * 8760 * (utilisation / 100) / 1000;
      const comparison = annualEnergy / annualBaseline * 100;
      const comparisonText = (comparison < 0.1 ? smallPercentFormat : percentFormat).format(comparison);
      energyTotal.textContent = `${energyFormat.format(annualEnergy)} TWh per year`;
      energyComparison.textContent = `${comparisonText}% of the fixed 286.8 TWh Australian 2025 comparison baseline, using the power and utilisation you selected.`;
      energyPresets.forEach((button) => {
        button.setAttribute('aria-pressed', String(Number(button.dataset.gw) === power));
      });
    };

    energyCalculator.addEventListener('submit', (event) => {
      event.preventDefault();
      updateEnergy();
    });
    powerInput.addEventListener('input', updateEnergy);
    utilisationInput.addEventListener('input', updateEnergy);
    energyPresets.forEach((button) => {
      button.type = 'button';
      button.addEventListener('click', () => {
        powerInput.value = button.dataset.gw;
        updateEnergy();
      });
    });
    if (!powerInput.value) powerInput.value = '13';
    if (!utilisationInput.value) utilisationInput.value = '100';
    updateEnergy();
  }

  document.querySelectorAll('.connection-map').forEach((map) => {
    const scope = map.closest('.tool-panel') || map;
    const choices = Array.from(map.querySelectorAll('button[data-node]'))
      .map((button) => ({ button, detail: document.getElementById(`node-${button.dataset.node}`) }))
      .filter((choice) => choice.detail && scope.contains(choice.detail));

    if (!choices.length) return;

    const showChoice = (selected) => {
      choices.forEach((choice) => {
        const active = choice === selected;
        choice.button.setAttribute('aria-pressed', String(active));
        choice.button.setAttribute('aria-controls', choice.detail.id);
        choice.detail.hidden = !active;
      });
    };

    choices.forEach((choice) => {
      choice.button.type = 'button';
      choice.button.addEventListener('click', () => showChoice(choice));
    });
    showChoice(choices.find((choice) => choice.button.getAttribute('aria-pressed') === 'true') || choices[0]);
  });

  // Escape closes the native menu while preserving ordinary link behaviour.
  document.querySelectorAll('.main-nav details').forEach((menu) => {
    menu.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && menu.open) {
        menu.open = false;
        const summary = menu.querySelector('summary');
        if (summary) summary.focus();
      }
    });
    menu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => { menu.open = false; });
    });
  });
})();
