import SwiftUI
let spring = Spring(duration: 0.5, bounce: 0)
let duration = spring.settlingDuration(target: 1.0, epsilon: 0.001)
print(duration)
print((0...100).map { i in String(format:"%.6f", i == 100 ? 1.0 : spring.value(target: 1.0, time: Double(i)/100 * duration)) }.joined(separator:", "))
