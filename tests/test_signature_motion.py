"""V1.1.0 motion contracts: finite timing, original artwork, no unverified awards."""
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class SignatureMotionTests(unittest.TestCase):
    def test_homepage_has_real_laser_perimeter_and_logo_halo(self):
        html = (DOCS / "index.html").read_text()
        self.assertIn('class="hero motion-hero"', html)
        self.assertIn('class="hero-laser-svg"', html)
        self.assertIn('class="hero-laser-trace"', html)
        self.assertIn('class="hero-laser-head"', html)
        self.assertIn('class="hero-logo-halo"', html)
        self.assertIn('src="assets/1ad-logo.svg"', html)
        self.assertIn('href="assets/motion-v11.css?v=2"', html)
        self.assertNotIn("fictional-match-result", html)

    def test_one_time_sequenced_effects_are_optional_and_accessible(self):
        css = (DOCS / "assets/motion-v11.css").read_text()
        for key in ("laser-outline-once", "laser-tip-once",
                    "logo-orbit-once", "logo-glint-once",
                    "weekly-crown-arrive", "weekly-champion-glow",
                    "champion-avatar-orbit-once"):
            self.assertIn(key, css)
        self.assertIn("prefers-reduced-motion:reduce", css)
        self.assertIn("stroke-dasharray:0 100", css)
        self.assertIn("stroke-dasharray:100 0", css)
        self.assertIn("pathLength", (DOCS / "index.html").read_text())
        # Only the old generic sheen was infinite; it's expressly suppressed
        # on the new actual home hero.
        self.assertIn('.hero.motion-hero::after{content:none!important;animation:none!important}', css)
        finite = re.findall(r'animation:\s*[^;\n]+;', css)
        self.assertTrue(finite)
        self.assertFalse(any("infinite" in a for a in finite))
        self.assertIn('.weekly-podium-place.gold .weekly-crown{display:none}', css)
        self.assertIn('data-award-verified="true"', css)
        # The metallic sweep must be masked to the original 1AD SVG's alpha,
        # not clipped to a rectangular/circular element around the logo.
        self.assertIn('-webkit-mask-image:url("1ad-logo.svg");mask-image:url("1ad-logo.svg")', css)
        self.assertIn('width:88%;max-width:235px;aspect-ratio:1', css)
        self.assertIn('.hero.motion-hero .hero-logo-halo::after{width:90%}', css)
        self.assertNotIn('clip-path:circle(50% at 50%)', css)
        self.assertIn('background-position:0% 50%', css)
        # Keep first-place ranking separate from the crown even at 320px.
        self.assertIn('.weekly-podium-place.gold .weekly-rank{', css)
        self.assertIn('position:relative;padding-top:60px', css)
        self.assertIn('width:56px;height:42px;margin:0 auto 4px', css)
        self.assertNotIn('margin:-18px auto -3px', css)
        # The circular portrait sheen starts at .12s, ends at .97s;
        # the crown must not start until AFTER that orbit is complete.
        self.assertIn('animation:champion-avatar-orbit-once .85s ease-out .12s 1 both', css)
        self.assertIn('animation:weekly-crown-arrive .8s cubic-bezier(.16,.89,.18,1.15) 1.05s 1 forwards', css)
        # Replaying the crown must also restart its avatar sheen, not just the crown.
        self.assertIn('.motion-replay .weekly-avatar::before{animation:none!important}', css)
        # The original 1AD emblem stays legible on narrow viewports, instead
        # of appearing semi-transparent underneath the hero headline.
        self.assertIn('.hero.motion-hero .hero-graphic{position:relative;top:auto;right:auto;', css)

    def test_weekly_production_bound_podium_has_no_winner_or_crown(self):
        html = (DOCS / "weekly.html").read_text()
        self.assertIn('data-award-verified="false"', html)
        self.assertIn('class="weekly-crown"', html)
        self.assertIn('No fictional winners', html)
        self.assertEqual(html.count('Awaiting results'), 3)
        self.assertNotIn('data-award-verified="true"', html)
        self.assertNotIn("RavenActual", html)

    def test_isolated_visual_lab_is_not_a_weekly_award(self):
        lab = (DOCS / "motion-review.html").read_text()
        self.assertIn("STAGING-ONLY MOTION PROTOTYPE", lab)
        self.assertIn("NO WEEKLY AWARD HAS BEEN GIVEN", lab)
        self.assertIn("Not a real winner", lab)
        self.assertIn('data-award-verified="true"', lab)
        self.assertIn("Replay hero trace", lab)
        self.assertIn("Replay sample crown", lab)
        self.assertIn('src="assets/1ad-logo.svg"', lab)
        self.assertIn("prefers-reduced-motion", (DOCS / "assets/motion-v11.css").read_text())
        entry = (DOCS / "staging-review.html").read_text()
        self.assertIn('href="motion-review.html"', entry)


if __name__ == "__main__":
    unittest.main()
