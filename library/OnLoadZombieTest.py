# Test for the arrival of the Necropolice

import OnLoadOneShot

class OnLoadZombieTest(OnLoadOneShot):
    def event(self):
        # Have we stopped being a zombie yet?
        return not self.on_load_parent.is_zombie()

    def action(self):
        # If we have stopped being a zombie, we should be taken to the
        # Necropolis
        p = self.on_load_parent
        p.message("You are taken by the Necropolice to the Necropolis")
        p.teleport_to(Position(0, 0, 'necropolis'))
