import { StrictMode } from 'react'
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { demoServer } from './demo-server'

// Uses real fetch, the actual React app, and a real FastAPI process. jsdom
// supplies the DOM; layout and actual browser CORS need the manual checklist.
describe.runIf(process.env.MATCHPULSE_RUN_API_TESTS === '1')(
  'connected demo rehearsal',
  () => {
    let server: Awaited<ReturnType<typeof demoServer>> | undefined

    afterEach(async () => {
      cleanup()
      vi.restoreAllMocks()
      vi.unstubAllEnvs()
      await server?.stop()
      server = undefined
    })

    async function mount(provider: 'mock' | 'fallback' = 'mock') {
      server = await demoServer(provider)
      await server.start()
      vi.stubEnv('VITE_API_BASE_URL', server.url)
      vi.resetModules()
      const { default: App } = await import('../src/App')
      const transport = vi.spyOn(globalThis, 'fetch')
      render(
        <StrictMode>
          <App />
        </StrictMode>,
      )
      return transport
    }

    const click = (name: string | RegExp) =>
      fireEvent.click(screen.getByRole('button', { name }))
    const select = (id: string) => click(new RegExp(id + '$'))
    const traces = () =>
      [...document.querySelectorAll('#agent-workflow pre')].map((element) =>
        JSON.parse(element.textContent!),
      )
    async function ready(id: string, provider = 'MOCK · RUNTIME') {
      await waitFor(
        () => {
          expect(
            document.querySelector('.selected-event-heading code')?.textContent,
          ).toBe(id)
          expect(screen.getByTestId('provenance').textContent).toBe(provider)
          expect(
            document
              .querySelector('.insight-column')
              ?.getAttribute('aria-busy'),
          ).toBe('false')
        },
        { timeout: 5000 },
      )
    }
    const metric = (id: string) => screen.getByTestId(id).textContent

    it('rehearses personalization, evidence, failed/missing/regain events, filters, and rewind without accumulating statistics', async () => {
      const transport = await mount()
      const posts = () =>
        transport.mock.calls.filter(([url]) =>
          String(url).endsWith('/events/process'),
        )
      await ready('evt-064')
      expect(posts()).toHaveLength(1) // StrictMode still sends one processing call.
      expect(metric('pass-length')).toBe('44.28')
      expect(metric('progression')).toBe('+40')
      expect(metric('lines-bypassed')).toBe('1')
      expect(metric('passes-atlas')).toBe('4/4')
      expect(metric('passes-harbor')).toBe('0/0')
      expect(traces().map((step) => step.agent)).toEqual([
        'match_intelligence',
        'tactical_explainer',
        'trust_personalization',
      ])
      expect(
        traces().every(
          (step) => step.status === 'completed' && step.duration_ms >= 0,
        ),
      ).toBe(true)
      fireEvent.click(screen.getByRole('tab', { name: /^Evidence/ }))
      const evidence = screen.getByRole('tabpanel', { name: /^Evidence/ })
      expect(
        within(evidence).getByRole('rowheader', { name: 'forward_progression' })
          .nextElementSibling?.textContent,
      ).toBe('40')
      expect(
        within(evidence).getByRole('rowheader', { name: 'successful' })
          .nextElementSibling?.textContent,
      ).toBe('True')
      fireEvent.keyDown(screen.getByRole('tab', { name: /^Evidence/ }), {
        key: 'End',
      })
      expect(
        screen
          .getByRole('tab', { name: 'Trust notes' })
          .getAttribute('aria-selected'),
      ).toBe('true')
      expect(document.activeElement).toBe(
        screen.getByRole('tab', { name: 'Trust notes' }),
      )
      fireEvent.keyDown(document.activeElement!, { key: 'Home' })
      expect(
        screen
          .getByRole('tab', { name: 'Insight' })
          .getAttribute('aria-selected'),
      ).toBe('true')
      const originalFacts = traces()[0].output
      const originalNarrative = traces()[2].output.insight

      click('Fan')
      click('Français')
      await ready('evt-064', 'MOCK · EXÉCUTION')
      expect(document.documentElement.lang).toBe('fr')
      expect(metric('pass-length')).toBe('44,28')
      expect(metric('progression')).toBe('+40')
      expect(traces()[0].output).toEqual(originalFacts)
      expect(traces()[2].output).toMatchObject({
        audience: 'fan',
        language: 'fr',
      })
      expect(traces()[2].output.insight).not.toEqual(originalNarrative)
      click('English')
      click('Analyst')
      await ready('evt-064')
      expect(screen.getByText('Cached API result')).toBeTruthy()

      select('evt-065')
      await ready('evt-065')
      expect(metric('passes-atlas')).toBe('4/5')
      expect(
        document.querySelector('.selected-event-heading')?.textContent,
      ).toContain('Unsuccessful pass')
      expect(traces()[1].output.candidate.interpretation).toBe('attempt_failed')
      select('evt-067')
      await ready('evt-067')
      expect(metric('progression')).toBe('+16') // Harbor attacks right to left.
      expect(metric('lines-bypassed')).toBe('?')
      expect(screen.getByText('Limited context')).toBeTruthy()
      expect(document.querySelector('.pitch-options')?.textContent).toContain(
        'Unknown',
      )
      expect(traces()[2].output.validation.status).toBe('limited')

      select('evt-066')
      await ready('evt-066')
      expect(metric('pass-length')).toBe('—')
      expect(metric('progression')).toBe('—')
      expect(metric('lines-bypassed')).toBe('—')
      expect(screen.queryByTestId('pass-trajectory')).toBeNull()
      expect(screen.getByTestId('point-overlay')).toBeTruthy()
      select('evt-068')
      await ready('evt-068')
      expect(metric('passes-atlas')).toBe('4/5')
      expect(metric('passes-harbor')).toBe('1/1')
      expect(screen.getByText('80%')).toBeTruthy()
      expect(screen.getByText('100%')).toBeTruthy()

      const beforeFilter = posts().length
      fireEvent.change(
        screen.getByRole('textbox', { name: 'Find an event or player' }),
        { target: { value: 'no-such-player' } },
      )
      expect(screen.getByText('No events match your filters.')).toBeTruthy()
      click('Clear filters')
      expect(
        screen.getAllByRole('button', { name: /evt-06[1-8]$/ }),
      ).toHaveLength(8)
      fireEvent.change(screen.getByRole('combobox', { name: 'Event type' }), {
        target: { value: 'interception' },
      })
      expect(
        screen.getAllByRole('button', { name: /evt-06[1-8]$/ }),
      ).toHaveLength(1)
      expect(screen.getByRole('button', { name: /evt-066$/ })).toBeTruthy()
      fireEvent.change(screen.getByRole('combobox', { name: 'Event type' }), {
        target: { value: 'all' },
      })
      expect(posts()).toHaveLength(beforeFilter)
      select('evt-064')
      await ready('evt-064')
      expect(screen.getByText('Cached API result')).toBeTruthy()
      expect(posts()).toHaveLength(beforeFilter)
      expect(metric('passes-atlas')).toBe('4/4')
      click('Run analysis again')
      expect(metric('pass-length')).toBe('—') // Old facts are hidden while pending.
      await ready('evt-064')
      expect(posts()).toHaveLength(beforeFilter + 1)
      expect(screen.getByText('New API result')).toBeTruthy()
      expect(metric('passes-atlas')).toBe('4/4')
    }, 20000)

    it('shows a real API outage, opens samples explicitly, and reconnects after FastAPI restarts', async () => {
      const transport = await mount()
      await ready('evt-064')
      await server!.stop()
      click('Run analysis again')
      await screen.findByRole(
        'heading',
        { name: 'This event could not be processed' },
        { timeout: 5000 },
      )
      expect(screen.getByTestId('provenance').textContent).toBe('API WORKSPACE')
      expect(metric('pass-length')).toBe('—')
      expect(document.querySelector('#analysis-panel')).toBeNull()
      expect(document.querySelectorAll('#agent-workflow pre')).toHaveLength(0)
      expect(screen.queryByText('SAMPLE DATA')).toBeNull()
      const beforeSamples = transport.mock.calls.length
      click('Use sample data')
      await waitFor(() =>
        expect(screen.getByTestId('provenance').textContent).toBe(
          'SAMPLE DATA',
        ),
      )
      select('evt-067')
      expect(metric('lines-bypassed')).toBe('?')
      expect(transport.mock.calls.length).toBe(beforeSamples)
      await server!.start()
      click('API mode')
      await ready('evt-064')
      expect(metric('pass-length')).toBe('44.28')
      expect(screen.getByText('New API result')).toBeTruthy()
    }, 20000)

    it('labels actual backend configuration fallback and exposes its provider reason', async () => {
      await mount('fallback')
      await ready('evt-064', 'MOCK FALLBACK')
      expect(metric('pass-length')).toBe('44.28')
      expect(traces()[1].output).toMatchObject({
        requested_provider: 'azure',
        actual_provider: 'mock',
        fallback_reason: 'azure_configuration',
        attempts: [{ provider: 'mock', status: 'completed' }],
      })
      fireEvent.click(screen.getByRole('tab', { name: 'Trust notes' }))
      expect(
        screen.getByText(
          'Azure configuration is incomplete or invalid; used the mock fallback without sending an Azure request.',
        ),
      ).toBeTruthy()
      expect(screen.queryByText('AZURE · RUNTIME')).toBeNull()
    }, 15000)
  },
)
