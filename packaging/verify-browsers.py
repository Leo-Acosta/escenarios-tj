"""Isolated browser acceptance against synthetic data, never a personal profile."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

def run(base, job, report, output):
    output.mkdir(parents=True,exist_ok=False)
    results=[]
    with sync_playwright() as p:
        for name in ('chromium','firefox'):
            entry={'engine':name,'synthetic':True,'errors':[]}
            browser=getattr(p,name).launch(headless=True)
            entry['version']=browser.version
            page=browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1)
            page.on('pageerror',lambda e:entry['errors'].append(str(e)))
            try:
                page.goto(base+'/app/',wait_until='networkidle')
                page.locator('.selection select').nth(0).select_option(index=1)
                page.locator('.selection select').nth(1).select_option('1')
                page.locator('.science-3d summary').wait_for(timeout=60000)
                page.locator('.science-3d summary').click()
                iframe=page.locator('.science-3d iframe')
                iframe.scroll_into_view_if_needed()
                frame=iframe.element_handle().content_frame()
                frame.wait_for_selector('.js-plotly-plot canvas',timeout=60000)
                frame.wait_for_function("document.querySelector('.js-plotly-plot')._fullLayout.scene._scene.glplot",timeout=60000)
                read_camera="JSON.stringify(document.querySelector('.js-plotly-plot')._fullLayout.scene._scene.getCamera())"
                before=frame.evaluate(read_camera)
                box=iframe.bounding_box()
                page.mouse.move(box['x']+box['width']*.5,box['y']+box['height']*.5)
                page.mouse.down();page.mouse.move(box['x']+box['width']*.68,box['y']+box['height']*.62,steps=20);page.mouse.up()
                page.wait_for_timeout(500)
                after=frame.evaluate(read_camera)
                assert before!=after,'La cámara 3D no cambia al arrastrar.'
                entry['rotation_verified']=True
                page.screenshot(path=str(output/(name+'-3d.png')))
                page.get_by_role('button',name='Verificar reproducción',exact=True).click()
                page.get_by_text('Reproducción verificada, sin nueva inferencia.',exact=True).wait_for(timeout=30000)
                entry['replay_verified']=True
                page.set_viewport_size({'width':390,'height':844})
                page.wait_for_timeout(500)
                entry['mobile_overflow_px']=page.evaluate('Math.max(0,document.documentElement.scrollWidth-window.innerWidth)')
                assert entry['mobile_overflow_px']<=2,'Desbordamiento horizontal en móvil.'
                page.screenshot(path=str(output/(name+'-mobile.png')))
                for label,url in [('scientific','/api/scientific/report?id='+job),('executive','/api/executive/html?id='+report)]:
                    page.goto(base+url,wait_until='networkidle')
                    page.emulate_media(media='print')
                    entry[label+'_print_toolbar_hidden']=not page.locator('button').first.is_visible()
                    assert entry[label+'_print_toolbar_hidden']
                    page.set_viewport_size({'width':794,'height':1123})
                    page.screenshot(path=str(output/(name+'-'+label+'-print.png')),full_page=True)
                    if name=='chromium':
                        target=output/(label+'-a4.pdf')
                        page.pdf(path=str(target),format='A4',prefer_css_page_size=True,print_background=True)
                        pdf=PdfReader(target)
                        assert all(abs(float(x.mediabox.width)-595.276)<1 and abs(float(x.mediabox.height)-841.89)<1 for x in pdf.pages)
                        assert 'DATOS SINTÉTICOS' in ' '.join(x.extract_text() for x in pdf.pages)
                        entry[label+'_a4_pages']=len(pdf.pages)
                entry['passed']=not entry['errors']
            except Exception as e:
                entry['passed']=False;entry['failure']=str(e)
                page.screenshot(path=str(output/(name+'-failure.png')))
            finally:browser.close()
            results.append(entry)
    (output/'browser-verification.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(results,ensure_ascii=False))
    return all(x['passed'] for x in results)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--base',required=True);a.add_argument('--job',required=True);a.add_argument('--report',required=True);a.add_argument('--output',type=Path,required=True)
    o=a.parse_args();raise SystemExit(0 if run(o.base,o.job,o.report,o.output) else 1)
