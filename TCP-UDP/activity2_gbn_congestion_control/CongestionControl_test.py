#!/usr/bin/env python3
"""
Test para la clase CongestionControl.
Verifica el comportamiento de slow start, congestion avoidance y timeouts.
"""

from CongestionControl import CongestionControl


def test_initialization():
    """Test 1: Verificar inicializacion correcta"""
    print("=" * 60)
    print("TEST 1: Inicializacion")
    print("=" * 60)

    MSS = 8
    cc = CongestionControl(MSS)

    assert cc.get_cwnd() == MSS, f"cwnd inicial deberia ser {MSS}, es {cc.get_cwnd()}"
    assert cc.get_ssthresh() is None, "ssthresh inicial deberia ser None"
    assert cc.is_state_slow_start(), "Estado inicial deberia ser slow_start"
    assert not cc.is_state_congestion_avoidance(), "No deberia estar en congestion_avoidance"
    assert cc.get_MSS_in_cwnd() == 1, "Deberia haber 1 MSS en cwnd inicialmente"

    print(f"✓ Inicializacion correcta: {cc}")
    print()


def test_slow_start():
    """Test 2: Verificar crecimiento en slow start"""
    print("=" * 60)
    print("TEST 2: Slow Start (sin ssthresh definido)")
    print("=" * 60)

    MSS = 8
    cc = CongestionControl(MSS)

    print(f"Inicial: {cc}")

    # Simular recepcion de ACKs en slow start
    for i in range(5):
        cc.event_ack_received()
        expected_cwnd = MSS * (i + 2)  # +1 MSS por cada ACK
        print(f"ACK {i+1}: cwnd={cc.get_cwnd()}B ({cc.get_MSS_in_cwnd()} MSS)")
        assert cc.get_cwnd() == expected_cwnd, f"cwnd deberia ser {expected_cwnd}"
        assert cc.is_state_slow_start(), "Deberia seguir en slow_start"

    print("✓ Slow start funciona correctamente")
    print()


def test_first_timeout():
    """Test 3: Verificar primer timeout (define ssthresh)"""
    print("=" * 60)
    print("TEST 3: Primer Timeout")
    print("=" * 60)

    MSS = 8
    cc = CongestionControl(MSS)

    # Crecer cwnd
    for _ in range(3):
        cc.event_ack_received()

    cwnd_before = cc.get_cwnd()
    print(f"Antes del timeout: cwnd={cwnd_before}B ({cc.get_MSS_in_cwnd()} MSS)")

    # Primer timeout
    cc.event_timeout()

    expected_ssthresh = cwnd_before // 2
    print(f"Despues del timeout: {cc}")

    assert cc.get_ssthresh() == expected_ssthresh, f"ssthresh deberia ser {expected_ssthresh}"
    assert cc.get_cwnd() == MSS, "cwnd deberia volver a 1 MSS"
    assert cc.is_state_slow_start(), "Deberia volver a slow_start"

    print("✓ Primer timeout define ssthresh correctamente")
    print()


def test_transition_to_congestion_avoidance():
    """Test 4: Verificar transicion a congestion avoidance"""
    print("=" * 60)
    print("TEST 4: Transicion a Congestion Avoidance")
    print("=" * 60)

    MSS = 8
    cc = CongestionControl(MSS)

    # Crecer hasta cwnd = 4 MSS, luego timeout
    for _ in range(3):
        cc.event_ack_received()

    cc.event_timeout()  # ssthresh = 16 (4*MSS/2 = 2MSS)
    ssthresh = cc.get_ssthresh()
    print(f"Despues de timeout: ssthresh={ssthresh}B, cwnd={cc.get_cwnd()}B")

    # Crecer en slow start hasta alcanzar ssthresh
    acks_needed = 0
    while cc.is_state_slow_start():
        cc.event_ack_received()
        acks_needed += 1
        print(f"  ACK {acks_needed}: cwnd={cc.get_cwnd()}B, estado={cc.current_state}")

    print(f"Transicion a AIMD despues de {acks_needed} ACKs")
    assert cc.is_state_congestion_avoidance(), "Deberia estar en congestion_avoidance"
    assert cc.get_cwnd() >= ssthresh, "cwnd deberia ser >= ssthresh"

    print("✓ Transicion a congestion avoidance correcta")
    print()


def test_congestion_avoidance_growth():
    """Test 5: Verificar crecimiento en congestion avoidance (AIMD)"""
    print("=" * 60)
    print("TEST 5: Congestion Avoidance (AIMD)")
    print("=" * 60)

    MSS = 8
    cc = CongestionControl(MSS)

    # Forzar entrada a congestion avoidance
    cc.cwnd = 32  # 4 MSS
    cc.ssthresh = 32
    cc.current_state = CongestionControl.CONGESTION_AVOIDANCE

    print(f"Inicial (AIMD): cwnd={cc.get_cwnd()}B ({cc.get_MSS_in_cwnd()} MSS)")

    # En AIMD: +1 MSS cada cwnd ACKs
    # Con cwnd=4 MSS, necesitamos 4 ACKs para aumentar en 1 MSS
    cwnd_before = cc.get_cwnd()
    mss_in_cwnd = cc.get_MSS_in_cwnd()

    for i in range(mss_in_cwnd):
        cc.event_ack_received()
        print(f"  ACK {i+1}: cwnd={cc.get_cwnd()}B")

    # Despues de mss_in_cwnd ACKs, deberia haber crecido aproximadamente 1 MSS
    # (puede ser menos por truncamiento de integers)
    print(f"Despues de {mss_in_cwnd} ACKs: cwnd creció de {cwnd_before}B a {cc.get_cwnd()}B")
    assert cc.get_cwnd() >= cwnd_before, "cwnd deberia haber crecido"

    print("✓ Crecimiento AIMD funciona")
    print()


def test_timeout_in_congestion_avoidance():
    """Test 6: Verificar timeout durante congestion avoidance"""
    print("=" * 60)
    print("TEST 6: Timeout en Congestion Avoidance")
    print("=" * 60)

    MSS = 8
    cc = CongestionControl(MSS)

    # Forzar estado AIMD con valores conocidos
    cc.cwnd = 64  # 8 MSS
    cc.ssthresh = 32
    cc.current_state = CongestionControl.CONGESTION_AVOIDANCE

    cwnd_before = cc.get_cwnd()
    print(f"Antes del timeout: {cc}")

    cc.event_timeout()

    expected_ssthresh = cwnd_before // 2
    print(f"Despues del timeout: {cc}")

    assert cc.get_ssthresh() == expected_ssthresh, f"ssthresh deberia ser {expected_ssthresh}"
    assert cc.get_cwnd() == MSS, "cwnd deberia volver a 1 MSS"
    assert cc.is_state_slow_start(), "Deberia volver a slow_start"

    print("✓ Timeout en AIMD funciona correctamente")
    print()


def test_different_mss():
    """Test 7: Probar con diferentes valores de MSS"""
    print("=" * 60)
    print("TEST 7: Diferentes valores de MSS")
    print("=" * 60)

    for MSS in [4, 8, 16, 32]:
        print(f"\nProbando con MSS={MSS}:")
        cc = CongestionControl(MSS)

        # Verificar inicializacion
        assert cc.get_cwnd() == MSS
        assert cc.get_MSS_in_cwnd() == 1

        # Crecer un poco
        cc.event_ack_received()
        assert cc.get_cwnd() == 2 * MSS
        assert cc.get_MSS_in_cwnd() == 2

        print(f"  ✓ MSS={MSS} funciona correctamente")

    print("\n✓ Diferentes MSS funcionan correctamente")
    print()


def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "=" * 60)
    print("TESTS PARA CONGESTIONCONTROL")
    print("=" * 60 + "\n")

    test_initialization()
    test_slow_start()
    test_first_timeout()
    test_transition_to_congestion_avoidance()
    test_congestion_avoidance_growth()
    test_timeout_in_congestion_avoidance()
    test_different_mss()

    print("=" * 60)
    print("✓ TODOS LOS TESTS PASARON")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
